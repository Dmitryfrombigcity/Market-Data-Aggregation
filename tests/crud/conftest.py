import datetime
import subprocess
from time import sleep
from typing import Iterator, AsyncIterator

import pytest
from loguru import logger
from psycopg import AsyncConnection

from src.db.connection import connection

query = """                                                                                                            
        CREATE TABLE test_table(                                                                                       
        id int PRIMARY KEY GENERATED ALWAYS AS IDENTITY,                                                               
        date date,                                                                                                     
        ticker varchar                                                                                                 
        );                                                                                                             
        """
insert_data = """                                                                                                      
        INSERT INTO test_table(                                                                                        
        date,                                                                                                          
        ticker                                                                                                         
        ) VALUES (%s,%s);                                                                                              
        """
data = ('2020-1-1', 'SBER')
read = """                                                                                                             
        SELECT * FROM test_table                                                                                       
        """
data_result = [(1, datetime.date(2020, 1, 1), 'SBER')]


@pytest.fixture(scope='module', autouse=True)
def start_db() -> Iterator[None]:
    subprocess.run('docker compose -f docker_for_tests.yml up -d', shell=True, capture_output=True)
    sleep(5)
    try:
        yield
    finally:
        subprocess.run('docker compose -f docker_for_tests.yml down', shell=True, capture_output=True)


@pytest.fixture(scope='function')
async def set_connection() -> AsyncIterator[AsyncConnection]:
    logger.remove()
    pool = await anext(connection)
    async with pool.connection() as aconn:
        yield aconn


@pytest.fixture(scope='function', autouse=True)
async def clean_after_test() -> AsyncIterator[None]:
    yield
    pool = await anext(connection)
    async with pool.connection() as aconn:
        await aconn.execute(
            """DROP TABLE IF EXISTS test_table;"""
        )
