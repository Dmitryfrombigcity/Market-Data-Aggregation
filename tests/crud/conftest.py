import subprocess
from pathlib import Path
from time import sleep
from typing import Iterator, AsyncIterator

import pytest
from loguru import logger
from psycopg import AsyncConnection

from src.db.connection import connection


@pytest.fixture(scope='module')
def start_db() -> Iterator[None]:
    # path = Path(Path(__file__).resolve().parent.parent / 'docker_for_tests.yml')
    # subprocess.run(
    #     f'docker compose -f{path} up -d',
    #     shell=True,
    #     capture_output=True
    # )
    # sleep(5)
    # try:
    #     yield
    # finally:
    #     subprocess.run(
    #         f'docker compose -f{path} down',
    #         shell=True,
    #         capture_output=True
    #     )
    yield


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
