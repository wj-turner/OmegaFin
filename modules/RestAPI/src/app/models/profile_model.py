from sqlalchemy import Column, Integer, String, Boolean, Float, BigInteger, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from .base import Base

class UserProfile(Base):
    __tablename__ = 'user_profiles'

    id = Column(Integer, primary_key=True)
    login = Column(BigInteger, nullable=False, unique=True)  # Added unique=True here
    trade_mode = Column(Integer)
    leverage = Column(Integer)
    limit_orders = Column(Integer)
    margin_so_mode = Column(Integer)
    trade_allowed = Column(Boolean)
    trade_expert = Column(Boolean)
    margin_mode = Column(Integer)
    currency_digits = Column(Integer)
    fifo_close = Column(Boolean)
    balance = Column(Float)
    credit = Column(Float)
    profit = Column(Float)
    equity = Column(Float)
    margin = Column(Float)
    margin_free = Column(Float)
    margin_level = Column(Float)
    margin_so_call = Column(Float)
    margin_so_so = Column(Float)
    margin_initial = Column(Float)
    margin_maintenance = Column(Float)
    assets = Column(Float)
    liabilities = Column(Float)
    commission_blocked = Column(Float)
    name = Column(String(255))
    server = Column(String(255))
    currency = Column(String(10))
    company = Column(String(255))
    last_update_date = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
