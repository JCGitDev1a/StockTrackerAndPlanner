from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass

from app.models.user import User  # noqa: E402,F401
from app.models.account import Account  # noqa: E402,F401
from app.models.security import Security  # noqa: E402,F401
from app.models.account_position import AccountPosition  # noqa: E402,F401
from app.models.transaction import Transaction  # noqa: E402,F401
from app.models.market_data_cache import MarketDataCache  # noqa: E402,F401
from app.models.price_history import PriceHistory  # noqa: E402,F401
from app.models.dividend_event import DividendEvent  # noqa: E402,F401
from app.models.company_profile import CompanyProfile  # noqa: E402,F401
