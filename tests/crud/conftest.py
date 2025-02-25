import subprocess
from time import sleep
from typing import Iterator, AsyncIterator

import pytest
from loguru import logger
from psycopg import AsyncConnection

from src.db.connection import connection


@pytest.fixture(scope='module')
def start_db() -> Iterator[None]:
    subprocess.run(
        'docker compose -f docker_for_tests.yml up -d',
        shell=True,
        capture_output=True
    )
    sleep(5)
    try:
        yield
    finally:
        subprocess.run(
            'docker compose -f docker_for_tests.yml down',
            shell=True,
            capture_output=True
        )


@pytest.fixture(scope='function')
async def set_connection() -> AsyncIterator[AsyncConnection]:
    logger.remove()
    pool = await anext(connection)
    async with pool.connection() as aconn:
        await aconn.set_autocommit(True)
        yield aconn


@pytest.fixture(scope='function')
async def clean_after_test() -> AsyncIterator[None]:
    yield
    pool = await anext(connection)
    async with pool.connection() as aconn:
        await aconn.execute(
            """DROP TABLE IF EXISTS test_table, results_of_trades, dividends, processed_data;"""
        )
