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

app = FastAPI(title="Stock Tracker and Planner API")

app.include_router(auth_router)
app.include_router(accounts_router)
app.include_router(securities_router)
app.include_router(positions_router)
app.include_router(transactions_router)
app.include_router(holdings_router)

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/health/db")
def database_health_check(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"database": "ok"}
