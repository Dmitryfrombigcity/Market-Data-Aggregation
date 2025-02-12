from typing import Any, NamedTuple, Iterable

from loguru import logger
from psycopg.abc import Query
from psycopg.errors import Error, DuplicateTable
from psycopg.rows import namedtuple_row

from src.db.connection import connection
from src.db.queries import truncate_processed_data


async def db_update(
        query: str,
        data: Iterable[tuple[Any, ...]]
) -> None:
    pool = await anext(connection)
    try:
        async with pool.connection() as aconn:
            async with aconn.cursor() as acur:
                await acur.executemany(query, data)
    except Error as err:
        logger.exception(err)
        raise


async def db_create(query: str) -> None:
    pool = await anext(connection)
    try:
        async with pool.connection() as aconn:
            await aconn.execute(query)
    except DuplicateTable:
        await db_update(truncate_processed_data, [()])
    except Error as err:
        logger.exception(err)
        raise


async def db_read(
        query: Query,
        data: tuple[Any, ...] | dict[str, Any] = tuple()
) -> list[NamedTuple]:
    pool = await anext(connection)
    try:
        async with pool.connection() as aconn:
            async with aconn.cursor(row_factory=namedtuple_row) as acur:
                await acur.execute(query, data)
                return await acur.fetchall()

    except Error as err:
        logger.exception(err)
        raise
