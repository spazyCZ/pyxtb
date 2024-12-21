import os
import json
from pyxtb.api import Api
from pyxtb._types import (
    ChartLastInfoRecord,
    ChartRangeInfoRecord,
    Cmd,
    Period,
    TradeTransInfoRecord,
    TransactionType,
)

async def fetch_and_store_data():
    api = Api(1000000, "password", "pyxtb", demo=True)
    await api.login()

    data = {}

    data['get_all_symbols'] = await api.get_all_symbols()
    data['get_calendar'] = await api.get_calendar()
    data['get_chart_last_request'] = await api.get_chart_last_request(
        ChartLastInfoRecord(
            period=Period.PERIOD_M5,
            start=int((datetime.datetime.now() - datetime.timedelta(days=1)).timestamp() * 1000),
            symbol="EURPLN",
        )
    )
    data['get_chart_range_request'] = await api.get_chart_range_request(
        ChartRangeInfoRecord(
            period=Period.PERIOD_M5,
            start=int((datetime.datetime.now() - datetime.timedelta(days=1)).timestamp() * 1000),
            end=int(datetime.datetime.now().timestamp() * 1000),
            ticks=None,
            symbol="EURPLN",
        )
    )
    data['get_commission_def'] = await api.get_commission_def("EURPLN", 1)
    data['get_current_user_data'] = await api.get_current_user_data()
    data['get_ibs_history'] = await api.get_ibs_history(
        start=int((datetime.datetime.now() - datetime.timedelta(days=1)).timestamp() * 1000),
        end=int(datetime.datetime.now().timestamp() * 1000),
    )
    data['get_margin_level'] = await api.get_margin_level()
    data['get_margin_trade'] = await api.get_margin_trade("EURPLN", 1)
    data['get_news'] = await api.get_news(
        start=int((datetime.datetime.now() - datetime.timedelta(days=1)).timestamp() * 1000)
    )
    data['get_profit_calculation'] = await api.get_profit_calculation(
        closePrice=1.3000, cmd=Cmd.BUY, openPrice=1.2233, symbol="EURPLN", volume=1.0
    )
    data['get_server_time'] = await api.get_server_time()
    data['get_step_rules'] = await api.get_step_rules()
    data['get_symbol'] = await api.get_symbol("EURPLN")
    data['get_tick_prices'] = await api.get_tick_prices(
        level=0, symbols=["EURPLN"], timestamp=int((datetime.datetime.now() - datetime.timedelta(minutes=5)).timestamp() * 1000)
    )
    data['get_trade_records'] = await api.get_trade_records([7489839])
    data['get_trades'] = await api.get_trades(True)
    data['get_trades_history'] = await api.get_trades_history(
        start=int((datetime.datetime.now() - datetime.timedelta(days=1)).timestamp() * 1000)
    )
    data['get_trading_hours'] = await api.get_trading_hours(["EURPLN"])
    data['get_version'] = await api.get_version()
    data['ping'] = await api.ping()
    data['trade_transaction'] = await api.trade_transaction(
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
    data['trade_transaction_status'] = await api.trade_transaction_status(data['trade_transaction']['order'])

    os.makedirs('mock_data', exist_ok=True)
    for key, value in data.items():
        with open(f'mock_data/{key}.json', 'w') as f:
            json.dump(value, f, indent=4)

    await api.logout()

if __name__ == "__main__":
    import asyncio
    asyncio.run(fetch_and_store_data())
