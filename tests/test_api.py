import pytest
import pytest_asyncio
from pyxtb.api import Api

@pytest_asyncio.fixture
async def api():
    api = Api(1000000, "password", "pyxtb", demo=True)
    await api.login()
    yield api
    await api.logout()

@pytest.mark.asyncio
async def test_login(api):
    assert api._logged_in is True

@pytest.mark.asyncio
async def test_get_all_symbols(api):
    symbols = await api.get_all_symbols()
    assert isinstance(symbols, list)
    assert len(symbols) > 0
    assert "symbol" in symbols[0].__dict__

@pytest.mark.asyncio
async def test_get_calendar(api):
    calendar = await api.get_calendar()
    assert isinstance(calendar, list)
    assert len(calendar) > 0
    assert "title" in calendar[0].__dict__
