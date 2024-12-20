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

@pytest.mark.asyncio
async def test_get_chart_last_request(api):
    response = await api.get_chart_last_request(
        ChartLastInfoRecord(
            period=Period.PERIOD_M5,
            start=int((datetime.datetime.now() - datetime.timedelta(days=1)).timestamp() * 1000),
            symbol="EURPLN",
        )
    )
    assert isinstance(response, dict)
    assert "rateInfos" in response

@pytest.mark.asyncio
async def test_get_chart_range_request(api):
    response = await api.get_chart_range_request(
        ChartRangeInfoRecord(
            period=Period.PERIOD_M5,
            start=int((datetime.datetime.now() - datetime.timedelta(days=1)).timestamp() * 1000),
            end=int(datetime.datetime.now().timestamp() * 1000),
            ticks=None,
            symbol="EURPLN",
        )
    )
    assert isinstance(response, dict)
    assert "rateInfos" in response

@pytest.mark.asyncio
async def test_get_commission_def(api):
    response = await api.get_commission_def("EURPLN", 1)
    assert isinstance(response, dict)
    assert "commission" in response

@pytest.mark.asyncio
async def test_get_current_user_data(api):
    response = await api.get_current_user_data()
    assert isinstance(response, dict)
    assert "currency" in response

@pytest.mark.asyncio
async def test_get_ibs_history(api):
    response = await api.get_ibs_history(
        start=int((datetime.datetime.now() - datetime.timedelta(days=1)).timestamp() * 1000),
        end=int(datetime.datetime.now().timestamp() * 1000),
    )
    assert isinstance(response, list)
    assert len(response) > 0
    assert "symbol" in response[0].__dict__

@pytest.mark.asyncio
async def test_get_margin_level(api):
    response = await api.get_margin_level()
    assert isinstance(response, dict)
    assert "balance" in response

@pytest.mark.asyncio
async def test_get_margin_trade(api):
    response = await api.get_margin_trade("EURPLN", 1)
    assert isinstance(response, dict)
    assert "margin" in response

@pytest.mark.asyncio
async def test_get_news(api):
    response = await api.get_news(
        start=int((datetime.datetime.now() - datetime.timedelta(days=1)).timestamp() * 1000)
    )
    assert isinstance(response, list)
    assert len(response) > 0
    assert "title" in response[0].__dict__

@pytest.mark.asyncio
async def test_get_profit_calculation(api):
    response = await api.get_profit_calculation(
        closePrice=1.3000, cmd=Cmd.BUY, openPrice=1.2233, symbol="EURPLN", volume=1.0
    )
    assert isinstance(response, dict)
    assert "profit" in response

@pytest.mark.asyncio
async def test_get_server_time(api):
    response = await api.get_server_time()
    assert isinstance(response, dict)
    assert "time" in response

@pytest.mark.asyncio
async def test_get_step_rules(api):
    response = await api.get_step_rules()
    assert isinstance(response, list)
    assert len(response) > 0
    assert "id" in response[0].__dict__

@pytest.mark.asyncio
async def test_get_symbol(api):
    response = await api.get_symbol("EURPLN")
    assert isinstance(response, dict)
    assert "symbol" in response

@pytest.mark.asyncio
async def test_get_tick_prices(api):
    response = await api.get_tick_prices(
        level=0, symbols=["EURPLN"], timestamp=int((datetime.datetime.now() - datetime.timedelta(minutes=5)).timestamp() * 1000)
    )
    assert isinstance(response, dict)
    assert "quotations" in response

@pytest.mark.asyncio
async def test_get_trade_records(api):
    response = await api.get_trade_records([7489839])
    assert isinstance(response, list)
    assert len(response) > 0
    assert "order" in response[0].__dict__

@pytest.mark.asyncio
async def test_get_trades(api):
    response = await api.get_trades(True)
    assert isinstance(response, list)
    assert len(response) > 0
    assert "order" in response[0].__dict__

@pytest.mark.asyncio
async def test_get_trades_history(api):
    response = await api.get_trades_history(
        start=int((datetime.datetime.now() - datetime.timedelta(days=1)).timestamp() * 1000)
    )
    assert isinstance(response, list)
    assert len(response) > 0
    assert "order" in response[0].__dict__

@pytest.mark.asyncio
async def test_get_trading_hours(api):
    response = await api.get_trading_hours(["EURPLN"])
    assert isinstance(response, list)
    assert len(response) > 0
    assert "symbol" in response[0].__dict__

@pytest.mark.asyncio
async def test_get_version(api):
    response = await api.get_version()
    assert isinstance(response, dict)
    assert "version" in response

@pytest.mark.asyncio
async def test_ping(api):
    response = await api.ping()
    assert response is None

@pytest.mark.asyncio
async def test_trade_transaction(api):
    trade_response = await api.trade_transaction(
        TradeTransInfoRecord(
            cmd=Cmd.BUY,
            customComment="Test",
            expiration=int((datetime.datetime.now() + datetime.timedelta(days=1)).timestamp() * 1000),
            offset=0,
            order=0,
            price=4.50,
            symbol="EURPLN",
            sl=0,
            tp=0,
            type=TransactionType.OPEN,
            volume=0.01
        )
    )
    assert isinstance(trade_response, dict)
    assert "order" in trade_response

@pytest.mark.asyncio
async def test_trade_transaction_status(api):
    trade_response = await api.trade_transaction(
        TradeTransInfoRecord(
            cmd=Cmd.BUY,
            customComment="Test",
            expiration=int((datetime.datetime.now() + datetime.timedelta(days=1)).timestamp() * 1000),
            offset=0,
            order=0,
            price=4.50,
            symbol="EURPLN",
            sl=0,
            tp=0,
            type=TransactionType.OPEN,
            volume=0.01
        )
    )
    response = await api.trade_transaction_status(trade_response["order"])
    assert isinstance(response, dict)
    assert "requestStatus" in response
