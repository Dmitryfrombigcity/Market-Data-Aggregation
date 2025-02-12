import asyncio
import sys
from asyncio import TaskGroup
from time import perf_counter
from typing import Any, Iterable

from loguru import logger

from logs.config import config
from project_settings import setting
from src.aiohttp.connection import connection
from src.data_collection import get_information, get_dividends, collect_information
from src.data_processing import data_processing
from src.db.crud import db_update, db_create
from src.db.queries import results_of_trades, dividends, insert_days_off_to_results_of_trades, processed_data


async def main(tickers: Iterable[str]) -> None:
    try:
        # collecting information from the website
        await db_create(results_of_trades)
        await db_create(dividends)
        await db_create(processed_data)

        tasks: list[asyncio.Task[Any]] = []
        async with asyncio.TaskGroup() as group:
            for ticker in tickers:
                tasks.append(
                    group.create_task(get_information(ticker))
                )
                group.create_task(get_dividends(ticker))
            for task in asyncio.as_completed(tasks):
                ticker, pages = await task
                group.create_task(collect_information(ticker, pages))

        # closing the session
        await connection.aclose()
        logger.info('Collecting information has completed')

        # modifying the collected information
        await db_update(insert_days_off_to_results_of_trades, [()])

        # processing of information
        async with TaskGroup() as group:
            for ticker in tickers:
                group.create_task(data_processing(ticker))
        logger.info('Processing of information has completed')

    except BaseException:
        print('>>> An error occurred. Please see the log.')


if __name__ == '__main__':
    logger.configure(**config)  # type:ignore
    tickers = setting.BUNCH_OF_TICKERS
    # with start_db():
    start = perf_counter()
    logger.info('Starting...')
    asyncio.run(main(tickers))
    logger.info('Ending...')
    print(perf_counter() - start)
