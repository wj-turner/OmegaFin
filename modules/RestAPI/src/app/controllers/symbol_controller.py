from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.symbol_model import Symbol
from typing import List
from ..models.base import Base
from pydantic import BaseModel

router = APIRouter()

# Create a Pydantic model for response
class SymbolResponse(BaseModel):
    id: int
    symbolId: int
    symbolName: str
    source: str
    initUntil: str
    enabled: int
    baseAssetId: int
    quoteAssetId: int
    symbolCategoryId: int
    description: str
# Create a Pydantic model for updating the enabled value
class UpdateEnabledValue(BaseModel):
    symbolName: str
    enabled: int

@router.get("/symbols/", response_model=List[SymbolResponse])
def read_symbols(db: Session = Depends(get_db)):
    symbols = db.query(Symbol).all()
    return symbols


@router.post("/price_initiation/")
def update_enabled_value(update_data: UpdateEnabledValue, db: Session = Depends(get_db)):
    # Get the symbol based on the provided name
    symbol = db.query(Symbol).filter(Symbol.symbolName == update_data.symbolName).first()

    # Check if the symbol exists
    if symbol:
        # Update the enabled value
        symbol.enabled = update_data.enabled
        db.commit()
        db.refresh(symbol)
        if update_data.enabled == 1:
            start_symbol_initiation(symbol)
        
        return {"message": "Enabled value updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="Symbol not found")
    

def start_symbol_initiation(symbol: Symbol):
    
    pass