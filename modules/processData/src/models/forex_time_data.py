from sqlalchemy import Column, Integer, String, Float, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ForexData(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True)
    pair_name = Column(String)
    time = Column(TIMESTAMP)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)

class OneMinData(ForexData):
    __tablename__ = 'one_min_data'
    
class fiveMinData(ForexData):
    __tablename__ = 'five_min_data'

# Repeat for 5min, 15min, etc.
