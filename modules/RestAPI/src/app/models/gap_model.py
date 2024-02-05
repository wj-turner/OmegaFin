
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

from .base import Base


class TimeDataGap(Base):
    __tablename__ = 'time_data_gap'
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String)
    start_date = Column(String)
    end_date = Column(String)
    timeframe = Column(String)
    status = Column(String)