from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from app.database import get_db
from app.models.symbol_model import Symbol
from app.models.deal_model import Deal
from app.models.position_model import Position
from app.models.app_config import AppConfig
from typing import List

router = APIRouter()


@router.get("/get_unsettled_risk/")
async def get_unsettled_risk(db: Session = Depends(get_db)):
    config = db.query(AppConfig).filter(AppConfig.config_key == 'initial_balance').first()
    if not config:
        raise HTTPException(status_code=404, detail="Initial balance config not found")
    
    try:
        initial_balance = float(config.config_value)
    except ValueError:
        raise HTTPException(status_code=500, detail="Invalid initial balance configuration")

    if initial_balance <= 0:
        raise HTTPException(status_code=400, detail="Initial balance must be positive")

    # Data aggregation and calculations
    open_positions_ids = db.query(Position.ticket).all()
    open_positions_set = {pos.ticket for pos in open_positions_ids}
    all_deals = db.query(Deal).filter(Deal.position_id.notin_(open_positions_set), Deal.position_id != 0)
    current_balance = initial_balance + sum(deal.profit + deal.swap + deal.commission + deal.fee for deal in all_deals)

    position_profits = db.query(
        Deal.position_id,
        func.sum(Deal.profit).label("total_profit")
    ).filter(Deal.position_id.notin_(open_positions_set)).group_by(Deal.position_id).all()

    threshold = initial_balance * 0.01
    last_loss = None
    for position_id, total_profit in sorted(position_profits, key=lambda x: x.position_id, reverse=True):
        if total_profit < -threshold:
            last_loss = (position_id, total_profit)
            break

    win_count = 0
    last_loss_id = last_loss[0] if last_loss else -1
    for position_id, total_profit in position_profits:
        if position_id > last_loss_id and total_profit > threshold:
            win_count += 1

    # Win count rotation logic
    win_count_rotated = win_count % 5

    # Risk calculation based on current balance and win count
    if current_balance >= initial_balance:
        if win_count_rotated == 0:
            risk_percentage = 1
        elif win_count_rotated == 1:
            risk_percentage = 2
        elif win_count_rotated in {2, 3, 4}:
            risk_base = current_balance
            risk_percentage = 2
        elif win_count_rotated == 5:
            risk_percentage = 1
        risk = risk_percentage * (initial_balance if win_count_rotated not in {2, 3, 4} else risk_base) / 100
    else:
        if win_count_rotated == 0 or win_count_rotated == 1:
            risk_percentage = 0.5
        elif win_count_rotated in {2, 3}:
            risk_percentage = 1
        elif win_count_rotated >= 4:
            risk_percentage = 2
        risk = risk_percentage * current_balance / 100

    # Response construction
    response = {
        "wins_after_last_loss": win_count,
        "last_loss": last_loss[1] if last_loss else None,
        "current_balance": current_balance,
        "risk": risk
    }

    return response

