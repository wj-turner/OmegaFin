from sqlalchemy import Column, BigInteger, String, Float, DateTime, Integer
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.ext.declarative import declarative_base
from .base import Base



class Order(Base):
    __tablename__ = 'orders'
    ticket = Column(BigInteger, primary_key=True)
    time_setup = Column(BigInteger)
    time_setup_msc = Column(BigInteger)
    time_done = Column(BigInteger)
    time_done_msc = Column(BigInteger)
    time_expiration = Column(BigInteger)
    type = Column(Integer)
    type_time = Column(Integer)
    type_filling = Column(Integer)
    state = Column(Integer)
    magic = Column(BigInteger)
    position_id = Column(BigInteger)
    position_by_id = Column(BigInteger)
    reason = Column(Integer)
    volume_initial = Column(Float)
    volume_current = Column(Float)
    price_open = Column(Float)
    sl = Column(Float)
    tp = Column(Float)
    price_current = Column(Float)
    price_stoplimit = Column(Float)
    symbol = Column(String)
    comment = Column(String)
    external_id = Column(String)
    # Additional fields based on your application's requirements
