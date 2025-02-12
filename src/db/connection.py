from typing import AsyncIterator

from psycopg_pool import AsyncConnectionPool

from src.db.config import setting


async def get_pool() -> AsyncIterator[AsyncConnectionPool]:
    async with AsyncConnectionPool(
            conninfo=setting.uri,
            open=False,
            timeout=5,
            max_size=setting.POOL_MAX_SIZE
    ) as pool:
        while True:
            yield pool


connection = get_pool()
