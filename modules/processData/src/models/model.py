from sqlalchemy import create_engine, Column, String, Numeric, TIMESTAMP, Integer, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base

# Create a single Base class
Base = declarative_base()

# Define the TickData model
class TickData(Base):
    __tablename__ = 'tick_data'
    pair_name = Column(String(50), primary_key=True)
    time = Column(TIMESTAMP, primary_key=True)
    source = Column(String)
    bid = Column(Numeric)
    ask = Column(Numeric)

    def __repr__(self):
        return f"<TickData(pair_name='{self.pair_name}', time='{self.time}', bid={self.bid}, ask={self.ask})>"

# Abstract class for OHLC data
class TimeData(Base):
    __abstract__ = True
    time = Column(TIMESTAMP, primary_key=True)
    pair_name = Column(String(50), primary_key=True)
    source = Column(String)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)

# OHLC models
class OneMinData(TimeData):
    __tablename__ = 'one_min_data'

class FiveMinData(TimeData):
    __tablename__ = 'five_min_data'

class FifteenMinData(TimeData):
    __tablename__ = 'fifteen_min_data'

class ThirtyMinData(TimeData):
    __tablename__ = 'thirty_min_data'

class OneHourData(TimeData):
    __tablename__ = 'one_hour_data'

class FourHourData(TimeData):
    __tablename__ = 'four_hour_data'

class OneDayData(TimeData):
    __tablename__ = 'one_day_data'

class OneWeekData(TimeData):
    __tablename__ = 'one_week_data'

class OneMonthData(TimeData):
    __tablename__ = 'one_month_data'


    

