import asyncio
import sys

import pytest
from _pytest.fixtures import FixtureFunction
from psycopg import sql
from psycopg.errors import DuplicateTable

from project_settings import setting
from src.data_processing import data_processing
from src.db.crud import db_create, db_update, db_read
from src.db.queries import results_of_trades, insert_days_off_to_results_of_trades, insert_results_of_trades, dividends, \
    insert_dividends, processed_data
from tests.crud.data.day_offs import data_with_day_offs, data_without_day_offs, final_data
from tests.crud.data.queries import query, insert_data, data, read, data_result, read_days_off, dividends_lst

pytestmark = pytest.mark.asyncio(loop_scope="module")

# if sys.platform == "win32":
#     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@pytest.mark.usefixtures("start_db", "clean_after_test")
class TestDatabase:
    async def test_create_db(self, set_connection: FixtureFunction) -> None:
        await db_create(query)
        with pytest.raises(DuplicateTable) as exc:
            await set_connection.execute(query)
        assert exc.type is DuplicateTable

    async def test_db_update(self, set_connection: FixtureFunction) -> None:
        async with set_connection.cursor() as acur:
            await acur.execute(query)
            await db_update(insert_data, [data])
            read_ = sql.SQL(read).format(
                table=sql.Identifier('test_table'))
            await acur.execute(read_)
            assert await acur.fetchall() == data_result

    async def test_db_read(self, set_connection: FixtureFunction) -> None:
        async with set_connection.cursor() as acur:
            await acur.execute(query)
            await acur.execute(insert_data, data)
            read_ = sql.SQL(read).format(
                table=sql.Identifier('test_table'))
            assert await db_read(read_) == data_result

    async def test_insert_day_offs(self, set_connection: FixtureFunction) -> None:
        await db_create(results_of_trades)
        await db_update(insert_results_of_trades, data_without_day_offs)
        await db_update(insert_days_off_to_results_of_trades, [()])
        assert await db_read(read_days_off) == data_with_day_offs

    async def test_data_processing(self, set_connection: FixtureFunction) -> None:
        async with set_connection.cursor() as acur:
            await acur.execute(results_of_trades)
            await acur.executemany(insert_results_of_trades, data_without_day_offs)
            await acur.execute(insert_days_off_to_results_of_trades)
            await acur.execute(dividends)
            await acur.executemany(insert_dividends, dividends_lst)
            await acur.execute(processed_data)
            await data_processing(setting.BUNCH_OF_TICKERS[0])
            read_ = sql.SQL(read).format(
                table=sql.Identifier('processed_data'))
            await acur.execute(read_)
            assert await acur.fetchall() == final_data
