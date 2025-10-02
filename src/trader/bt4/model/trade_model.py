import uuid
from datetime import datetime
from typing import Any, List, Optional

from sqlalchemy import ARRAY, JSON, Boolean, DateTime, Float, ForeignKey, Integer, Numeric, PickleType, String, Text, \
    CHAR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bt4.Constants import CandleType, ExType, QItem
from bt4.model.postgresql_mgr import Base
from bt4.model.state_model import TradeState, BalanceState


def generate_str_uuid():
    uid = str(uuid.uuid4())
    return uid

def restore_enums(cfg_rules):
    cfg_rules["cdl_type"] = CandleType(cfg_rules["cdl_type"])
    for var in cfg_rules["vars"]:
        cfg_rules["vars"][var]["cdl_type"] = CandleType(cfg_rules["vars"][var]["cdl_type"])
        qitems = []
        for src in cfg_rules["vars"][var]["sources"]:
            qitems.append(QItem(src))
        cfg_rules["vars"][var]["sources"] = qitems

    return cfg_rules



class TRSummary(Base):
    __tablename__ = "trade_summary"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement = True)
    summary_uuid: Mapped[str] = mapped_column(String, unique = True, default = generate_str_uuid)
    tid : Mapped[int] = mapped_column(ForeignKey("trade_request.tid"), nullable = True)
    op_type: Mapped[str] = mapped_column(String(60))  ##bt, ft, lt
    bt_start : Mapped[DateTime] = mapped_column(DateTime())
    bt_end : Mapped[DateTime] = mapped_column(DateTime())
    markets: Mapped[Text] = mapped_column(Text())
    last_balance : Mapped[Numeric] = mapped_column(Numeric(), nullable = True, default = 0)
    max_bal: Mapped[str] = mapped_column(String(60), nullable = True, default = "0")
    init_bal: Mapped[str] = mapped_column(String(60), nullable = True, default = "0")
    trade_win_rate: Mapped[str] = mapped_column(String(60), nullable = True, default = "0.0")
    num_of_trades: Mapped[str] = mapped_column(String(60), nullable = True, default = "0.0")
    num_of_wins: Mapped[str] = mapped_column(String(60),nullable = True, default = "0.0")
    num_of_loses: Mapped[str] = mapped_column(String(60),nullable = True, default = "0.0")
    profit_sum: Mapped[str] = mapped_column(String(60), nullable = True, default = "0.0")
    invest_sum: Mapped[str] = mapped_column(String(60), nullable = True, default = "0.0")
    avg_profit_ratio: Mapped[str] = mapped_column(String(60), nullable = True, default = "0.0")
    num_1_pcnt: Mapped[str] = mapped_column(String(60), nullable = True, default = "0.0")
    num_2_pcnt: Mapped[str] = mapped_column(String(60), nullable = True, default = "0.0")
    num_3_pcnt: Mapped[str] = mapped_column(String(60), nullable = True, default = "0.0")
    num_5_pcnt: Mapped[str] = mapped_column(String(60), nullable = True, default = "0.0")
    settle_winning_rate: Mapped[str] = mapped_column(String(60), nullable = True, default = "0.0")
    settle_total_trade: Mapped[str] = mapped_column(String(60), nullable = True, default = "0.0")
    settle_winning: Mapped[str] = mapped_column(String(60), nullable = True, default = "0.0")
    settle_lose: Mapped[str] = mapped_column(String(60), nullable = True, default = "0.0")
    mdd : Mapped[str] = mapped_column(String(60),nullable = True, default = "0.0")
    mdd_10: Mapped[str] = mapped_column(String(60), nullable = True, default = "0")
    mdd_20: Mapped[str] = mapped_column(String(60), nullable = True, default = "0")
    twoXdur: Mapped[Text] = mapped_column(Text(), nullable = True, default = "0")
    mpr: Mapped[str] = mapped_column(String(60), nullable = True, default = "0")
    profit_std: Mapped[str] = mapped_column(String(60), nullable = True, default = "0")
    sharp_index: Mapped[str] = mapped_column(String(60), nullable = True, default = "0.0")
    result_df : Mapped[PickleType] = mapped_column(PickleType(), nullable = True)
    progress: Mapped[str] = mapped_column(String(60), nullable = True, default = "0.0")
    ga_params_json: Mapped[JSON] = mapped_column(JSON(), nullable = True)
    tr_req_json: Mapped[JSON] = mapped_column(JSON(), nullable = True)

    # balance_chart

    # trade_units: Mapped[List["BTTradeUnit"]] = relationship(
    #     back_populates="btsummary", cascade="all, delete-orphan"
    # )
    def __repr__(self) -> str:
        return f"BTSummary(id={self.id!r}, summary_uuid={self.summary_uuid!r}, bt_start={self.bt_start!r}, bt_end={self.bt_end!r})"


class TradeUnit(Base):
    __tablename__ = "trade_unit"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement = True)
    tid: Mapped[int] = mapped_column(ForeignKey("trade_request.tid"), nullable = True)
    tr_sum_id : Mapped[Optional[int]] = mapped_column(ForeignKey("trade_summary.id"), nullable = True)
    is_processed: Mapped[Boolean] = mapped_column(Boolean())
    order: Mapped[String] = mapped_column(String(10))
    date: Mapped[DateTime] = mapped_column(DateTime())
    market: Mapped[String] = mapped_column(String(10))
    evaluated_market_balance: Mapped[Float] = mapped_column(Float())
    settled_price: Mapped[Float] = mapped_column(Float())
    settled_vol: Mapped[Float] = mapped_column(Float())
    fee: Mapped[Float] = mapped_column(Float())
    market_cash_bal: Mapped[Float] = mapped_column(Float())
    cash_bal: Mapped[Float] = mapped_column(Float())
    profit: Mapped[Float] = mapped_column(Float())
    evaluated_balance: Mapped[Float] = mapped_column(Float())
    desc: Mapped[String] = mapped_column(String(5000))
    origin_id: Mapped[String] = mapped_column(String())


    def __repr__(self) -> str:
        return f"BTTradeUnit(id={self.id!r}, tr_sum_id={self.tr_sum_id!r})"


def generate_uuid():
    uid = str(uuid.uuid4())
    return uid

from sqlalchemy.dialects.postgresql import UUID

class TradingRequestTbl(Base):
    __tablename__ = "trade_request"
    tid: Mapped[int] = mapped_column(primary_key = True, autoincrement = True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    # sid: Mapped[str] = mapped_column(String(60), nullable = True)
    sid: Mapped[str] = mapped_column(String(60))
    user_id: Mapped[uuid.UUID] = mapped_column(UUID)
    user_id_first_char: Mapped[str] = mapped_column(CHAR(1))
    trade_request_uuid: Mapped[str] = mapped_column(String, unique=True, default=generate_uuid)
    stgy_name: Mapped[str] = mapped_column(String(60))
    op_type: Mapped[str] = mapped_column(String(60)) ##bt, ft, lt
    desc: Mapped[str] = mapped_column(String(60), nullable=True)
    period_type: Mapped[str] = mapped_column(String)
    bt_start: Mapped[str] = mapped_column(String)
    bt_end: Mapped[str] = mapped_column(String)
    op_type: Mapped[str] = mapped_column(String(60))
    ex_type: Mapped[str] = mapped_column(String(60))
    # cfg_stgy_rules_json: Mapped[JSONB] = mapped_column(JSONB(), nullable=True)
    cfg_stgy_rules_json: Mapped[JSON] = mapped_column(JSON(), nullable = True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now)

    trade_unit: Mapped[List[TradeUnit]] = relationship("TradeUnit")
    trade_summary: Mapped[TRSummary] = relationship("TRSummary")
    trade_state : Mapped[TradeState] = relationship("TradeState")
    balance_state: Mapped[BalanceState] = relationship("BalanceState")

    def __repr__(self) -> str :
        return f"Strategy(id={self.id!r})"


class UserExchangeApiKeyModel(Base):
    __tablename__ = "user_exchange_api_key"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[UUID] = mapped_column(UUID)
    ex_type: Mapped[ExType] = mapped_column(String)
    access_key: Mapped[str] = mapped_column(String)
    secret_key: Mapped[str] = mapped_column(String)
    exp_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    executable_ip_addresses: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=True)


class AIModel(Base):
    __tablename__ = "ai"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ex_type: Mapped[str] = mapped_column(String)
    market: Mapped[String] = mapped_column(String(10))
    category: Mapped[String] = mapped_column(String)
    candle_type: Mapped[CandleType] = mapped_column(Integer, nullable=True)
    model: Mapped[String] = mapped_column(String)
    seq_len: Mapped[int] = mapped_column(Integer)
    pred_len: Mapped[int] = mapped_column(Integer)
    performance: Mapped[str] = mapped_column(String, nullable=True)
    train_start: Mapped[DateTime] = mapped_column(DateTime(timezone=True))
    train_end: Mapped[DateTime] = mapped_column(DateTime(timezone=True))
    saved_model: Mapped[Any] = mapped_column(PickleType())
    saved_scaler: Mapped[Any] = mapped_column(PickleType())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now, onupdate=datetime.now)