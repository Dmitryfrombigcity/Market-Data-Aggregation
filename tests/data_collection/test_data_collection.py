from unittest.mock import MagicMock

import pytest
from aiohttp import ClientError

from src.data_collection import get_information, get_dividends

pytestmark = pytest.mark.asyncio(loop_scope="module")


@pytest.mark.usefixtures("mockers")
class TestDataCollection:
    @pytest.mark.parametrize(
        "start, page, mockers", [
            (0, 0, (0, 0)),
            (0, 1, (1, 0)),
            (1, 1, (0, 1)),
            (1, 1, (1, 1))
        ], indirect=["mockers"]
    )
    async def test_1(self, start: int, page: int) -> None:
        _, index = await get_information('', start)
        assert index.ind == page

    @pytest.mark.parametrize(
        "start, page, mockers", [
            (0, 0, (5, 5)),
        ], indirect=["mockers"]
    )
    async def test_2(self, mockers: MagicMock, start: int, page: int) -> None:
        mockers.side_effect = ClientError("BOOM")
        with pytest.raises(ClientError) as exc:
            await get_information('', start)
        assert exc.type is ClientError and "BOOM" == exc.value.args[0]

    @pytest.mark.parametrize(
        "mockers", [
            (0, 2),
            (1, 3),
            (2, 4),
        ], indirect=["mockers"]
    )
    async def test_3(self) -> None:
        await get_dividends('')

    @pytest.mark.parametrize(
        "mockers", [
            (5, 5),
        ], indirect=["mockers"]
    )
    async def test_4(self, mockers: MagicMock) -> None:
        mockers.side_effect = ClientError("BOOM")
        with pytest.raises(ClientError) as exc:
            await get_dividends('')
        assert exc.type is ClientError and "BOOM" == exc.value.args[0]
