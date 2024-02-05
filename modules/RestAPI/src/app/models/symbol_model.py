from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

from .base import Base


class Symbol(Base):
    __tablename__ = 'symbols'
    id = Column(Integer, primary_key=True, autoincrement=True)  # Primary key
    symbolId = Column(Integer, nullable=False, unique=True)
    symbolName = Column(String, nullable=False)
    source = Column(String, nullable=False)
    initUntil = Column(String)
    enabled = Column(Integer)
    baseAssetId = Column(Integer)
    quoteAssetId = Column(Integer)
    symbolCategoryId = Column(Integer)
    description = Column(String)