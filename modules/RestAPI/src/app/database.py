from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager 
from sqlalchemy.orm import Session

# Database connection URL
SQLALCHEMY_DATABASE_URL = "postgresql://forexuser:forexpassword@postgres:5432/configdb"

# Create the SQLAlchemy engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# SessionLocal class is used to create a session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative models
Base = declarative_base()

def get_db() -> Session:
    db = SessionLocal()  # Use your actual method for creating a session
    try:
        yield db
    finally:
        db.close()