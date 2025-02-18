from functools import partial
from typing import Any, NamedTuple, Unpack
from unittest.mock import MagicMock

import pytest
from _pytest.fixtures import FixtureRequest
from loguru import logger

from tests.data_collection.data.dividends import DIVIDENDS_0, DIVIDENDS_1, DIVIDENDS_3, DIVIDENDS_0_lst, DIVIDENDS_1_lst, \
    DIVIDENDS_3_lst
from tests.data_collection.data.moex_0 import MOEX_0_lst, MOEX_0
from tests.data_collection.data.moex_1 import MOEX_1_lst, MOEX_1

data_lst = [MOEX_0_lst, MOEX_1_lst, DIVIDENDS_0_lst, DIVIDENDS_1_lst, DIVIDENDS_3_lst]
data = [MOEX_0, MOEX_1, DIVIDENDS_0, DIVIDENDS_1, DIVIDENDS_3]


class Temp(NamedTuple):
    value: int


async def temp(ind: int, *args: Unpack[Any]) -> None:
    assert args[1] == data_lst[ind]


@pytest.fixture(scope='function')
async def mockers(request: FixtureRequest, mocker: MagicMock) -> Any:
    logger.remove()
    flag_inx, data_ind = request.param

    mock_response = mocker.MagicMock()
    mock_response.return_value.__aenter__.return_value.text.return_value = data[data_ind]
    mock_response.return_value.__aenter__.return_value.raise_for_status = mocker.MagicMock()

    mock_db_read = mocker.AsyncMock(
        return_value=(Temp(flag_inx),) if flag_inx else None
    )
    temp_ = partial(temp, data_ind)
    mock_db_update = mocker.AsyncMock(
        side_effect=temp_
    )

    mocker.patch("aiohttp.ClientSession.get", mock_response)
    mocker.patch("src.data_collection.db_read", mock_db_read)
    mocker.patch("src.data_collection.db_update", mock_db_update)

    return mock_response
