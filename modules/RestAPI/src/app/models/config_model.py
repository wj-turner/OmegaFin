from sqlalchemy import Column, Integer, String, Boolean, Float, BigInteger, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from .base import Base

class AppConfig(Base):
    __tablename__ = 'app_config'

    config_key = Column(String(255), primary_key=True)
    config_value = Column(String(255), nullable=False)
    description = Column(Text)

