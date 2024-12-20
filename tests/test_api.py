import pytest
import pytest_asyncio
from pyxtb.api import Api
from pyxtb._types import (
    ChartLastInfoRecord,
    ChartRangeInfoRecord,
    Cmd,
    Period,
    TradeTransInfoRecord,
    TransactionType,
)
import os
import json

@pytest_asyncio.fixture
async def api():
    api = Api(1000000, "password", "pyxtb", demo=True)
    await api.login()
    yield api
    await api.logout()

@pytest.fixture
def mock_data():
    data = {}
    for filename in os.listdir('mock_data'):
        with open(f'mock_data/{filename}', 'r') as f:
            data[filename.split('.')[0]] = json.load(f)
    return data

@pytest.mark.asyncio
async def test_login(api):
    assert api._logged_in is True

@pytest.mark.asyncio
async def test_get_all_symbols(api, mock_data):
    symbols = mock_data['get_all_symbols']
    assert isinstance(symbols, list)
    assert len(symbols) > 0
    assert "symbol" in symbols[0]

@pytest.mark.asyncio
async def test_get_calendar(api, mock_data):
    calendar = mock_data['get_calendar']
    assert isinstance(calendar, list)
    assert len(calendar) > 0
    assert "title" in calendar[0]

@pytest.mark.asyncio
async def test_get_chart_last_request(api, mock_data):
    response = mock_data['get_chart_last_request']
    assert isinstance(response, dict)
    assert "rateInfos" in response

@pytest.mark.asyncio
async def test_get_chart_range_request(api, mock_data):
    response = mock_data['get_chart_range_request']
    assert isinstance(response, dict)
    assert "rateInfos" in response

@pytest.mark.asyncio
async def test_get_commission_def(api, mock_data):
    response = mock_data['get_commission_def']
    assert isinstance(response, dict)
    assert "commission" in response

@pytest.mark.asyncio
async def test_get_current_user_data(api, mock_data):
    response = mock_data['get_current_user_data']
    assert isinstance(response, dict)
    assert "currency" in response

@pytest.mark.asyncio
async def test_get_ibs_history(api, mock_data):
    response = mock_data['get_ibs_history']
    assert isinstance(response, list)
    assert len(response) > 0
    assert "symbol" in response[0]

@pytest.mark.asyncio
async def test_get_margin_level(api, mock_data):
    response = mock_data['get_margin_level']
    assert isinstance(response, dict)
    assert "balance" in response

@pytest.mark.asyncio
async def test_get_margin_trade(api, mock_data):
    response = mock_data['get_margin_trade']
    assert isinstance(response, dict)
    assert "margin" in response

@pytest.mark.asyncio
async def test_get_news(api, mock_data):
    response = mock_data['get_news']
    assert isinstance(response, list)
    assert len(response) > 0
    assert "title" in response[0]

@pytest.mark.asyncio
async def test_get_profit_calculation(api, mock_data):
    response = mock_data['get_profit_calculation']
    assert isinstance(response, dict)
    assert "profit" in response

@pytest.mark.asyncio
async def test_get_server_time(api, mock_data):
    response = mock_data['get_server_time']
    assert isinstance(response, dict)
    assert "time" in response

@pytest.mark.asyncio
async def test_get_step_rules(api, mock_data):
    response = mock_data['get_step_rules']
    assert isinstance(response, list)
    assert len(response) > 0
    assert "id" in response[0]

@pytest.mark.asyncio
async def test_get_symbol(api, mock_data):
    response = mock_data['get_symbol']
    assert isinstance(response, dict)
    assert "symbol" in response

@pytest.mark.asyncio
async def test_get_tick_prices(api, mock_data):
    response = mock_data['get_tick_prices']
    assert isinstance(response, dict)
    assert "quotations" in response

@pytest.mark.asyncio
async def test_get_trade_records(api, mock_data):
    response = mock_data['get_trade_records']
    assert isinstance(response, list)
    assert len(response) > 0
    assert "order" in response[0]

@pytest.mark.asyncio
async def test_get_trades(api, mock_data):
    response = mock_data['get_trades']
    assert isinstance(response, list)
    assert len(response) > 0
    assert "order" in response[0]

@pytest.mark.asyncio
async def test_get_trades_history(api, mock_data):
    response = mock_data['get_trades_history']
    assert isinstance(response, list)
    assert len(response) > 0
    assert "order" in response[0]

@pytest.mark.asyncio
async def test_get_trading_hours(api, mock_data):
    response = mock_data['get_trading_hours']
    assert isinstance(response, list)
    assert len(response) > 0
    assert "symbol" in response[0]

@pytest.mark.asyncio
async def test_get_version(api, mock_data):
    response = mock_data['get_version']
    assert isinstance(response, dict)
    assert "version" in response

@pytest.mark.asyncio
async def test_ping(api, mock_data):
    response = mock_data['ping']
    assert response is None

@pytest.mark.asyncio
async def test_trade_transaction(api, mock_data):
    trade_response = mock_data['trade_transaction']
    assert isinstance(trade_response, dict)
    assert "order" in trade_response

@pytest.mark.asyncio
async def test_trade_transaction_status(api, mock_data):
    response = mock_data['trade_transaction_status']
    assert isinstance(response, dict)
    assert "requestStatus" in response
