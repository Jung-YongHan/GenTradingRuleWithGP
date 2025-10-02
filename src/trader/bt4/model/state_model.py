import uuid

from sqlalchemy.orm import Mapped, mapped_column

from bt4.model.postgresql_mgr import Base
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime


class TradeState(Base):
    __tablename__ = "trade_state"
    id: Mapped[int] = mapped_column(primary_key = True, autoincrement = True)
    tid: Mapped[int] = mapped_column(ForeignKey("trade_request.tid"), nullable = True)

    user_id: Mapped[uuid.UUID] = mapped_column(UUID)
    ex_type: Mapped[str] = mapped_column(String(60))
    datetime: Mapped[datetime] = mapped_column(DateTime(timezone = True), default = datetime.now)
    flag_stmt: Mapped[String] = mapped_column(String(2000))

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
    desc: Mapped[String] = mapped_column(String(1000))
    txid: Mapped[String] = mapped_column(String(1000))
    origin_id: Mapped[String] = mapped_column(String())
    def __repr__(self) -> str:
        return f"TradeState(id={self.id!r}, tid={self.tid!r}, user_id={self.user_id!r}, datetime={self.datetime!r}, is_processed={self.is_processed!r}, order={self.order!r})"

class BalanceState(Base):
    __tablename__ = "balance_state"
    id: Mapped[int] = mapped_column(primary_key = True, autoincrement = True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID)
    ex_type: Mapped[str] = mapped_column(String(60))
    tid: Mapped[int] = mapped_column(ForeignKey("trade_request.tid"), nullable = True)
    datetime: Mapped[DateTime] = mapped_column(DateTime(timezone = True), default = datetime.now)
    total : Mapped[Numeric] = mapped_column(Numeric())
    base_cur : Mapped[Numeric] = mapped_column(Numeric())
    market: Mapped[String] = mapped_column(String(10))
    market_vol: Mapped[Float] = mapped_column(Float())
    market_price : Mapped[Float] = mapped_column(Float())

