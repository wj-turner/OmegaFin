from sqlalchemy import Column, BigInteger, String, Float, DateTime, Integer
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.ext.declarative import declarative_base
from .base import Base



class Position(Base):
    __tablename__ = 'positions'
    ticket = Column(BigInteger, primary_key=True)
    time = Column(BigInteger)
    time_msc = Column(BigInteger)
    time_update = Column(BigInteger)
    time_update_msc = Column(BigInteger)
    type = Column(Integer)
    magic = Column(BigInteger)
    identifier = Column(BigInteger)
    reason = Column(Integer)
    volume = Column(Float)
    price_open = Column(Float)
    sl = Column(Float)
    tp = Column(Float)
    price_current = Column(Float)
    swap = Column(Float)
    profit = Column(Float)
    symbol = Column(String)
    comment = Column(String)
    external_id = Column(String)
