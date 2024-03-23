from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.symbol_model import Symbol
from app.models.gap_model import TimeDataGap
from typing import List
from ..models.base import Base
from pydantic import BaseModel
import pandas_market_calendars as mcal
import datetime

router = APIRouter()

timeframe_mapping = {
    "M1": (1, 1),
    "M2": (2, 2),
    "M3": (3, 3),
    "M4": (4, 4),
    "M5": (5, 5),
    "M10": (10, 6),
    "M15": (15, 7),
    "M30": (30, 8),
    "H1": (60, 9),
    "H4": (240, 10),
    "H12": (720, 11),
    "D1": (1440, 12),
    "W1": (10080, 13),
    "MN1": (43200, 14)  # Assuming 30 days in a month for simplicity
}
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
    symbol = db.query(Symbol).filter(Symbol.symbolName == update_data.symbolName).first()
    if symbol:
        symbol.enabled = update_data.enabled
        db.commit()
        db.refresh(symbol)
        if update_data.enabled == 1:
            start_symbol_initiation(symbol, db)
        return {"message": "Enabled value updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="Symbol not found")

def start_symbol_initiation(symbol: Symbol, db: Session):
    init_date = symbol.initUntil

    # Use the updated timeframe_mapping which includes both duration and IDs
    for timeframe_code, (minutes, timeframe_id) in timeframe_mapping.items():
        # Now, the calculate_ranges function expects a timeframe code ('M1', 'M2', etc.)
        ranges = calculate_ranges(init_date, timeframe_code)

        # The calculate_and_insert_ranges function now also expects a timeframe code, not just the ID
        for range_start, range_end in ranges:
            # Pass the timeframe_code directly; modification to handle IDs is within the function
            calculate_and_insert_ranges(symbol.symbolId, range_start, range_end, timeframe_code, db)
    
    # Update the symbol's initUntil to the current datetime after processing
    symbol.initUntil = datetime.datetime.now().strftime("%Y-%m-%d")
    db.commit()

def calculate_and_insert_ranges(symbol_id: int, range_start: datetime.datetime, range_end: datetime.datetime, timeframe_code: str, db: Session):
    _, timeframe_id = timeframe_mapping.get(timeframe_code, (None, None))
    if timeframe_id is None:
        raise ValueError(f"Unsupported timeframe code: {timeframe_code}")

    new_gap = TimeDataGap(
        symbol=symbol_id,
        start_date=str(int(range_start.timestamp()) * 1000),
        end_date=str(int(range_end.timestamp()) * 1000),
        timeframe=str(timeframe_id),  # Store the ID as a string
        status="pending"
    )
    db.add(new_gap)
    db.commit()


def calculate_ranges(init_date: str, timeframe_code: str):
    try:
        init_date = datetime.datetime.strptime(init_date, "%Y-%m-%d")
    except ValueError:
        init_date = datetime.datetime(1970, 1, 1)
    now = datetime.datetime.now()
    ranges = []

    if timeframe_code in timeframe_mapping:
        minutes, _ = timeframe_mapping[timeframe_code]
        delta = datetime.timedelta(minutes=5000 * minutes)
    else:
        raise ValueError(f"Unsupported timeframe: {timeframe_code}")

    start_date = init_date
    while start_date < now:
        end_date = min(start_date + delta, now)
        ranges.append((start_date, end_date))
        start_date = end_date + datetime.timedelta(seconds=1)

    return ranges




  # purpuse is to calculate date and insert start and end in database so later another process call api base on this data
    # 1)get init date for this symbol using symbol name from postgres db using symbol model
    # 2)foreach timeframes (Monthly, weekly, daily, 4 hour, 1 hour, 30 min, 15min, 5 min, 1min)+ (add 2 min, 3min, 4 min,... 1 hour)
    # 3)each request that we are going to call has a 5000 data row limit so the range must be less that a 5000. from init date 5000 timeframe next or if reach now.
    #   if reach 5000 limit add it to a list.for example if start date is 1970 and its daily start date is 1970 and end date is 5000 days later. like this until reach today.later we are going to use this list to populate a table in database.  
    # loop throu ranges list and add the data to gap table
    # update last init of the symbol