from sqlalchemy import Column, BigInteger, String, Float, DateTime, Integer
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.ext.declarative import declarative_base
from .base import Base



class Deal(Base):
    __tablename__ = 'deals'
    ticket = Column(BigInteger, primary_key=True)
    order = Column(BigInteger)
    time = Column(BigInteger)
    time_msc = Column(BigInteger)
    type = Column(Integer)
    entry = Column(Integer)
    magic = Column(BigInteger)
    position_id = Column(BigInteger)
    reason = Column(Integer)
    volume = Column(Float)
    price = Column(Float)
    commission = Column(Float)
    swap = Column(Float)
    profit = Column(Float)
    fee = Column(Float)
    symbol = Column(String)
    comment = Column(String)
    external_id = Column(String)
