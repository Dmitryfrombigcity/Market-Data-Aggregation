import pytest
from _pytest.fixtures import FixtureFunction
from psycopg.errors import DuplicateTable

from src.db.crud import db_create, db_update, db_read
from tests.crud.conftest import query, insert_data, read, data, data_result

pytestmark = pytest.mark.asyncio(loop_scope="module")


async def test_create_db(set_connection: FixtureFunction) -> None:
    await db_create(query)
    with pytest.raises(DuplicateTable) as exc:
        await set_connection.execute(query)
    assert exc.type is DuplicateTable


async def test_db_update(set_connection: FixtureFunction) -> None:
    async with set_connection.cursor() as acur:
        await acur.execute(query)
        await set_connection.commit()
        await db_update(insert_data, [data])
        await acur.execute(read)
        assert await acur.fetchall() == data_result


async def test_db_read(set_connection: FixtureFunction) -> None:
    async with set_connection.cursor() as acur:
        await acur.execute(query)
        await set_connection.commit()
        await acur.execute(insert_data, data)
        await set_connection.commit()
        assert await db_read(read) == data_result
