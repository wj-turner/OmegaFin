from sqlalchemy import create_engine, Column, String, Numeric, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class TickData(Base):
    __tablename__ = 'tick_data'
    pair_name = Column(String(10), primary_key=True)
    time = Column(TIMESTAMP, primary_key=True)
    bid = Column(Numeric)
    ask = Column(Numeric)

    def __repr__(self):
        return f"<TickData(pair_name='{self.pair_name}', time='{self.time}', bid={self.bid}, ask={self.ask})>"
