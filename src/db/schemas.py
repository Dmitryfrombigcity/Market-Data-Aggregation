import datetime
from decimal import Decimal
from typing import NamedTuple


class NewRecord(NamedTuple):
    trade_date: datetime.date
    ticker: str
    closing_price: Decimal


class Record(NewRecord):
    value: Decimal


class Flag(NamedTuple):
    value: int
