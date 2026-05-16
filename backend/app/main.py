from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.auth import router as auth_router
from app.db.session import get_db

from app.api.accounts import router as accounts_router
from app.api.securities import router as securities_router
from app.api.positions import router as positions_router
from app.api.transactions import router as transactions_router
from app.api.holdings import router as holdings_router
from app.api.market_data import router as market_data_router
from app.api.dividends import router as dividends_router

app = FastAPI(title="Stock Tracker and Planner API")

app.include_router(auth_router)
app.include_router(accounts_router)
app.include_router(securities_router)
app.include_router(positions_router)
app.include_router(transactions_router)
app.include_router(holdings_router)
app.include_router(market_data_router)
app.include_router(dividends_router)

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/health/db")
def database_health_check(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"database": "ok"}
