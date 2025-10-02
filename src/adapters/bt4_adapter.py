# adapters/bt4_adapter.py

import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Dict, Tuple

# bt4_trader 경로 추가
BT4_TRADER_PATH = os.environ.get(
    "BT4_TRADER_PATH", str(Path(__file__).parent.parent.parent.parent / "bt4_trader")
)

if os.path.exists(BT4_TRADER_PATH):
    sys.path.insert(0, BT4_TRADER_PATH)
else:
    raise ImportError(f"bt4_trader를 찾을 수 없습니다: {BT4_TRADER_PATH}")

try:
    from bt4 import GlobalProperties
    from bt4.Constants import ExType, Operation_Type, R
    from bt4.core.CfgStgyRuleGenerator import CfgStgyRuleGenerator
    from bt4.exec.BullTraderMain import BullTrader
    from bt4.resource_path_mgr import RPath
    from bt4.utils.python_utils import load_class_from_module
except ImportError as e:
    raise ImportError(f"bt4_trader 모듈을 임포트할 수 없습니다: {e}") from e


class BT4BacktestAdapter:
    """GP 전략을 bt4_trader로 평가하는 어댑터"""

    def __init__(self, base_config: Dict):
        """
        Args:
            base_config: 기본 백테스트 설정
                - markets: 거래 마켓 리스트
                - bt_start: 백테스트 시작일
                - bt_end: 백테스트 종료일
                - ex_type: 거래소 타입 (upbit, binance 등)
                - initial_balance: 초기 자본금
        """
        self.base_config = base_config
        self.evaluation_count = 0
        self.r = R()
        self.temp_dir = tempfile.mkdtemp(prefix="gp_bt4_")

    def __del__(self):
        """임시 디렉토리 정리"""
        if hasattr(self, "temp_dir") and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
            except Exception:
                pass

    def evaluate_strategy(self, gp_strategy_json: Dict) -> float:
        """
        GP가 생성한 전략 JSON을 평가

        Args:
            gp_strategy_json: GP에서 생성된 전략 JSON
                - vars: 지표 정의
                - buy_systems: 매수 조건
                - buy_system_op: 매수 조건 연산
                - sell_systems: 매도 조건
                - sell_system_op: 매도 조건 연산

        Returns:
            fitness_score: 적합도 점수
        """
        try:
            # 1. GP JSON을 bt4 형식으로 변환
            bt4_config = self._convert_gp_to_bt4_format(gp_strategy_json)

            # 2. 임시 전략 파일 생성
            temp_tid = -(self.evaluation_count + 1)
            self.evaluation_count += 1

            # 3. 백테스트 실행
            fitness = self._run_backtest(bt4_config, temp_tid)

            # 4. 임시 파일 정리
            self._cleanup_temp_files(temp_tid)

            return fitness

        except Exception as e:
            print(f"[BT4Adapter] 전략 평가 중 오류: {e}")
            import traceback

            traceback.print_exc()
            return -1000.0

    def _convert_gp_to_bt4_format(self, gp_json: Dict) -> Dict:
        """GP JSON을 bt4 형식으로 변환"""
        bt4_config = self.base_config.copy()

        # vars 변환
        if "vars" in gp_json:
            bt4_config["vars"] = self._convert_vars(gp_json["vars"])

        # buy_systems 변환
        if "buy_systems" in gp_json:
            bt4_config["buy_systems"] = gp_json["buy_systems"]

        if "buy_system_op" in gp_json:
            bt4_config["buy_system_op"] = gp_json["buy_system_op"]

        # sell_systems 변환
        if "sell_systems" in gp_json:
            bt4_config["sell_systems"] = gp_json["sell_systems"]

        if "sell_system_op" in gp_json:
            bt4_config["sell_system_op"] = gp_json["sell_system_op"]

        # 기본 필드 추가
        if "stgy_name" not in bt4_config:
            bt4_config["stgy_name"] = f"GPStrategy_{self.evaluation_count}"

        if "module_name" not in bt4_config:
            bt4_config["module_name"] = f"gp_temp_{self.evaluation_count}"

        return bt4_config

    def _convert_vars(self, gp_vars: Dict) -> Dict:
        """GP의 vars를 bt4 형식으로 변환"""
        bt4_vars = {}

        for var_name, var_data in gp_vars.items():
            bt4_vars[var_name] = {
                "func": var_data.get("func"),
                "params": var_data.get("params", []),
                "cdl_type": var_data.get("cdl_type", "period"),
                "sources": var_data.get("sources", ["close"]),
                "unary": var_data.get("unary", False),
            }

        return bt4_vars

    def _run_backtest(self, config: Dict, temp_tid: int) -> float:
        """백테스트 실행 및 적합도 계산"""
        try:
            # 1. 전략 파일 생성
            cfg_module = self._generate_temp_strategy(temp_tid, config)

            # 2. 백테스트 실행
            result_df = self._execute_backtest(cfg_module, temp_tid)

            # 3. 적합도 계산
            fitness = self._calculate_fitness(result_df)

            return fitness

        except Exception as e:
            print(f"[BT4Adapter] 백테스트 실행 중 오류: {e}")
            import traceback

            traceback.print_exc()
            return -1000.0

    def _generate_temp_strategy(self, temp_tid: int, config: Dict) -> str:
        """임시 전략 파일 생성"""
        ex_type = ExType(config.get("ex_type", "upbit"))
        module_name = f"gp_temp_{abs(temp_tid)}"
        config["module_name"] = module_name

        csr = CfgStgyRuleGenerator()
        _, _, cfg_module = csr.generate_cfg_stgy_rule(module_name, ex_type, config)

        return cfg_module

    def _execute_backtest(self, cfg_module: str, temp_tid: int) -> Tuple:
        """백테스트 실행"""
        GlobalProperties.tid = temp_tid
        parameters = {}

        # 설정 로드
        config = load_class_from_module(cfg_module, "Config")
        config.load_params(self.r, parameters)

        # 공통 설정 로드
        exchange = cfg_module.split(".")[1]
        comm_cfg_module = (
            f"{RPath.instance().bt_cfg_root_module()}."
            f"{exchange}.bt_{exchange}_common_conf"
        )
        comm_cls = f"Bt_{exchange}_CommonConfig"
        common_config = load_class_from_module(comm_cfg_module, comm_cls)
        common_config.load_params(self.r, parameters)

        parameters[self.r.OP.tid] = temp_tid
        parameters[self.r.OP.OP] = Operation_Type.BACK_TESTOR
        parameters[self.r.OP.cfg_module] = cfg_module

        # 백테스트 실행
        bullTrader = BullTrader()
        context = bullTrader.prepare(parameters)
        bullTrader.setup(context)
        bullTrader.start()

        result_df = (
            context.strategy.report.toDataFrame()
            if hasattr(context.strategy, "report")
            else None
        )

        return result_df

    def _calculate_fitness(self, result_df) -> float:
        """
        적합도 계산

        여러 지표를 조합하여 적합도 계산 가능:
        - 총 수익률
        - 샤프 비율
        - 최대 낙폭 (MDD)
        - 승률
        - 거래 횟수
        """
        if result_df is None or len(result_df) == 0:
            return -1000.0

        try:
            # 기본: 총 수익률 계산
            final_balance = result_df.iloc[-1]["evaluated_balance"]
            initial_balance = result_df.iloc[0]["evaluated_balance"]
            total_return = (final_balance - initial_balance) / initial_balance * 100

            # 더 복잡한 적합도 함수 구현 가능
            # - 샤프 비율 추가
            # - MDD 페널티 추가
            # - 거래 횟수 고려

            return total_return

        except Exception as e:
            print(f"[BT4Adapter] 적합도 계산 중 오류: {e}")
            import traceback

            traceback.print_exc()
            return -1000.0

    def _cleanup_temp_files(self, temp_tid: int):
        """임시로 생성된 파일 삭제"""
        try:
            module_name = f"gp_temp_{abs(temp_tid)}"
            stgy_root = RPath.instance().stgy_root()

            # 생성된 .py 파일들 삭제
            for ex in ["upbit", "binance", "bithumb"]:
                cfg_file = f"{stgy_root}/{ex}/{module_name}.py"
                stgy_file = f"{stgy_root}/{ex}/{module_name}_module.py"

                if os.path.exists(cfg_file):
                    os.remove(cfg_file)
                if os.path.exists(stgy_file):
                    os.remove(stgy_file)

            # __pycache__ 정리
            pycache_dir = f"{stgy_root}/__pycache__"
            if os.path.exists(pycache_dir):
                for file in os.listdir(pycache_dir):
                    if module_name in file:
                        os.remove(os.path.join(pycache_dir, file))

        except Exception:
            # 정리 실패는 무시 (성능에 영향 없음)
            pass
