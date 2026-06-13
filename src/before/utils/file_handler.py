# utils/file_handler.py

import json
import logging
import os
from datetime import datetime

import pydot
from deap import gp

from src.before.configs.constants import LOG_DIR


def setup_logging():
    """날짜별/실행별 폴더를 만들고 로거를 설정한 뒤, 결과 폴더 경로를 반환"""
    now = datetime.now()
    date_dir = os.path.join(LOG_DIR, now.strftime("%Y-%m-%d"))
    run_dir_name = "run_" + now.strftime("%H-%M-%S")
    output_dir = os.path.join(date_dir, run_dir_name)
    os.makedirs(output_dir, exist_ok=True)

    log_filepath = os.path.join(output_dir, "strategy.log")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_filepath, encoding="utf-8"),
            logging.StreamHandler(),
        ],
        force=True,
    )
    logging.info(f"결과가 '{output_dir}' 폴더에 저장됩니다.")
    return output_dir


def save_json_strategy(strategy_dict, output_dir):
    """최종 전략 딕셔너리를 JSON 파일로 저장"""
    filepath = os.path.join(output_dir, "strategy.json")
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(strategy_dict, f, indent=4, ensure_ascii=False)
        logging.info(f"💾 JSON 전략 저장 완료: '{filepath}'")
    except Exception as e:
        logging.error(f"❌ JSON 파일 저장 실패: {e}")


def visualize_tree(individual, output_dir):
    """GP 트리를 지정된 폴더에 PNG 파일로 저장"""
    filepath = os.path.join(output_dir, "strategy_tree.png")
    nodes, edges, labels = gp.graph(individual)
    graph = pydot.Dot(graph_type="graph", bgcolor="#f0f0f0")

    for node_idx, node_label in labels.items():
        fillcolor = "#ffffff"  # 기본색
        if node_label == "Strategy":
            fillcolor = "#c5e3c5"
        elif node_label.startswith("buy_system"):
            fillcolor = "#f2c5c5"
        elif node_label.startswith("sell_system"):
            fillcolor = "#c5d5e3"
        elif node_label in ["and_", "or_", "not_"]:
            fillcolor = "#e3d1c5"
        graph.add_node(
            pydot.Node(node_idx, label=node_label, style="filled", fillcolor=fillcolor)
        )

    for edge in edges:
        graph.add_edge(pydot.Edge(edge[0], edge[1]))
    try:
        graph.write_png(filepath)
        logging.info(f"📊 트리 시각화 완료: '{filepath}'")
    except OSError as e:
        logging.error(f"❌ 트리 시각화 실패: Graphviz를 찾을 수 없습니다. (오류: {e})")
