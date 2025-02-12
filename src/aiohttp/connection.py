from typing import AsyncGenerator

import aiohttp

from src.aiohttp.settings import HEADERS, setting


async def get_session() -> AsyncGenerator[aiohttp.ClientSession, None]:
    conn = aiohttp.TCPConnector(limit=setting.TCPConnectorLimit)
    timeout = aiohttp.ClientTimeout(total=None)
    async with aiohttp.ClientSession(
            headers=HEADERS,
            connector=conn,
            timeout=timeout
    ) as session:
        try:
            while True:
                yield session
        finally:
            print('closed')


connection = get_session()
