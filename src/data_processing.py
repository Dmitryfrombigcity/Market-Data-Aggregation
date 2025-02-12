from decimal import Decimal
from typing import cast

from project_settings import setting
from src.db.crud import db_read, db_update
from src.db.queries import data_for_calculation, get_next_record, insert_processed_data
from src.db.schemas import Record, NewRecord


async def data_processing(ticker: str) -> None:
    """processing of data according to specified settings"""

    # record: Record
    # next_record: NewRecord
    next_record_lst: list[NewRecord] = []

    data = cast(list[Record], await db_read(
        data_for_calculation, {
            'ticker': ticker,
            'dividends_purchase_day_offset': setting.DIVIDENDS_PURCHASE_DAY_OFFSET,
            'monthly_purchase_day': setting.MONTHLY_PURCHASE_DAY}
    ))  # to satisfy mypy

    shares = monthly_balance = expenses = Decimal(0)

    for record in data:
        price = record.closing_price
        date = record.trade_date
        if not record.closing_price:
            for _ in range(setting.LIMIT_OF_DAYS_FOR_PRICE_SEARCH):
                next_record_lst = cast(
                    list[NewRecord], await db_read(get_next_record, {'ticker': ticker, 'date': date})
                )  # to satisfy mypy
                if next_record_lst:
                    next_record, *_ = next_record_lst
                    if next_record.closing_price:
                        price = next_record.closing_price
                        date = next_record.trade_date
                        break
                    else:
                        date = next_record.trade_date
                        continue
                else:
                    break
            # end of records reached
            if not next_record_lst:
                break

        if not record.value:
            expenses += setting.MONTHLY_INVESTMENTS
            shares = shares + (setting.MONTHLY_INVESTMENTS + monthly_balance) // price
            monthly_balance = (setting.MONTHLY_INVESTMENTS + monthly_balance) % price
            capitalization = shares * price
        else:
            shares = shares + (record.value * shares + monthly_balance) // price
            monthly_balance = (record.value * shares + monthly_balance) % price
            capitalization = shares * price

        new_record = date, ticker, expenses, shares, capitalization, price, monthly_balance
        await db_update(insert_processed_data, (new_record,))
