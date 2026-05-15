from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.db.session import get_db
from app.models.security import Security
from app.models.user import User
from app.schemas.security import SecurityCreateRequest, SecurityResponse

router = APIRouter(prefix="/securities", tags=["securities"])


@router.post("", response_model=SecurityResponse, status_code=status.HTTP_201_CREATED)
def create_security(
    payload: SecurityCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    existing_security = (
        db.query(Security)
        .filter(Security.symbol == payload.symbol.upper())
        .first()
    )

    if existing_security:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security already exists",
        )

    security = Security(
        symbol=payload.symbol.upper(),
        company=payload.company,
        dividend_frequency=payload.dividend_frequency,
    )

    db.add(security)
    db.commit()
    db.refresh(security)

    return security


@router.get("", response_model=list[SecurityResponse])
def list_securities(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(Security).order_by(Security.symbol).all()


@router.get("/{security_id}", response_model=SecurityResponse)
def get_security(
    security_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    security = (
        db.query(Security)
        .filter(Security.id == security_id)
        .first()
    )

    if security is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Security not found",
        )

    return security
