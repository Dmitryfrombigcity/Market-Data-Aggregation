import subprocess
import sys
from contextlib import contextmanager
from time import sleep
from typing import Iterator, Type

from loguru import logger
from pydantic_core import ValidationError
from pydantic_settings import BaseSettings


@contextmanager
def start_db() -> Iterator[None]:
    """ database management"""
    subprocess.run('docker compose -f docker.yml up -d', shell=True)
    sleep(10)
    try:
        yield
    finally:
        subprocess.run('docker compose -f docker.yml down', shell=True)


def instantiate[T: BaseSettings](Settings: Type[T]) -> T:
    try:
        return Settings()
    except ValidationError as err:
        logger.remove()
        logger.add('logs/logging.txt')
        logger.exception(err)
        print(err)
        sys.exit(1)  # to avoid ImportError
