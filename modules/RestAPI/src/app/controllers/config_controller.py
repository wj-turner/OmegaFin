from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.config_model import AppConfig  # Adjust the import according to your project structure
from app.database import get_db
from ..models.base import Base
from pydantic import BaseModel

router = APIRouter()


class InitialBalance(BaseModel):
    balance: float
    
@router.post("/set_initial_balance/")
def set_initial_balance(balance_data: InitialBalance, db: Session = Depends(get_db)):
    # Check if the initial balance already exists
    config_entry = db.query(AppConfig).filter_by(config_key="initial_balance").first()
    if config_entry:
        # Update the existing entry
        config_entry.config_value = str(balance_data.balance)
    else:
        # Create a new config entry
        new_config = AppConfig(
            config_key="initial_balance",
            config_value=str(balance_data.balance),
            description="Initial balance for user accounts"
        )
        db.add(new_config)
    
    db.commit()
    return {"message": "Initial balance set successfully"}