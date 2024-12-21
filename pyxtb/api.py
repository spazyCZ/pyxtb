import asyncio
import json
import logging
from asyncio import StreamReader, StreamWriter, Task
from collections import defaultdict
from dataclasses import dataclass
from typing import Callable, TypeVar

from dataclasses_json import DataClassJsonMixin

from ._types import (
    LOGIN_RESPONSE,
    RESPONSE,
    CalendarRecord,
    ChartLastInfoRecord,
    ChartRangeInfoRecord,
    ChartResponseRecord,
    Command,
    CommissionDefResponseRecord,
    CurrentUserDataRecord,
    IBRecord,
    MarginLevelRecord,
    MarginTradeRecord,
    NewsTopicRecord,
    ProfitCalculationRecord,
    ServerTimeRecord,
    StepRuleRecord,
    StreamingBalanceRecord,
    StreamingCandleRecord,
    StreamingKeepAliveRecord,
    StreamingNewsRecord,
    StreamingProfitRecord,
    StreamingTickRecord,
    StreamingTradeRecord,
    StreamingTradeStatusRecord,
    SymbolRecord,
    TickPricesResponseRecord,
    Time,
    TradeRecord,
    TradeTransactionStatusResponseRecord,
    TradeTransInfoRecord,
    TradeTransResponseRecord,
    TradingHoursRecord,
    VersionRecord,
)
from .errors import handle_error

T = TypeVar("T")


logging.basicConfig(level=logging.INFO)

DEFAULT_XAPI_ADDRESS = "xapi.xtb.com"


class Api:
    """
    Main XTB API connector.

    Provides methods to interact with the XTB trading API, including authentication,
    data retrieval, and real-time streaming of trade information.

    Examples:
        >>> async with Api(1000000, "password") as api:
        >>>     trades = await api.get_trades(openedOnly=True)
        >>>     symbols = [await api.get_symbol(trade.symbol) for trade in trades]
        >>>     symbol_map = {symbol.symbol: symbol for symbol in symbols}
        >>>     print("Opened trades profit")
        >>>     for trade in trades:
        >>>         print(f"{symbol_map[trade.symbol].description}: {trade.profit}")
    
    Documentation:
        For more details, refer to the [XTB API Documentation](http://developers.xstore.pro/documentation/#overview).
    """

    @dataclass
    class _ConnectionInfo:
        port: int
        streaming: int

    _DEMO = _ConnectionInfo(port=5124, streaming=5125)
    _REAL = _ConnectionInfo(port=5112, streaming=5113)

    _address: str
    _logged_in: bool = False
    _reader: StreamReader | None = None
    _writer: StreamWriter | None = None
    _stream_session_id: str | None = None
    _streaming_reader: StreamReader | None = None
    _streaming_writer: StreamWriter | None = None
    _callbacks = defaultdict(list)
    _reading_task: Task | None = None
    _connection_info: _ConnectionInfo

    def __init__(
        self,
        login: int,
        password: str,
        app_name="pyxtb",
        address=DEFAULT_XAPI_ADDRESS,
        demo: bool = True,
    ):
        """
        Initialize Api object
        """

        self._login = login
        self._password = password
        self._app_name = app_name
        self._address = address
        self._connection_info = Api._DEMO if demo else Api._REAL

    async def __aenter__(self):
        """
        Asynchronous context manager entry.

        Logs into the API when entering the context.
        """
        await self.login()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        """
        Asynchronous context manager exit.

        Logs out of the API and closes connections when exiting the context.
        """
        if self._logged_in:
            await self.logout()
        for stream in [
            self._writer,
            self._streaming_writer,
        ]:
            if stream and stream.can_write_eof():
                stream.close()
                await stream.wait_closed()
        if self._reading_task:
            if self._reading_task.done():
                exception = self._reading_task.exception()
                if exception:
                    raise exception
            self._reading_task.cancel()
        return False

    async def _write_(self, writer: StreamWriter | None, data: str):
        """
        Writes data to the specified stream writer.

        Args:
            writer (StreamWriter | None): The stream writer to write data to.
            data (str): The data to write.
        """
        if not self._writer:
            raise Exception("Writer not set up")
        writer.write(data.encode())

    async def _read_(self, reader: StreamReader | None, buffer_size=4096) -> str:
        """
        Reads data from the specified stream reader.

        Args:
            reader (StreamReader | None): The stream reader to read data from.
            buffer_size (int, optional): The buffer size for reading data. Defaults to 4096.

        Returns:
            str: The read data as a string.
        """
        if not reader:
            raise Exception("Reader not set up")
        data = bytearray()
        while True:
            await asyncio.sleep(0.01)
            chunk = await reader.read(buffer_size)
            data += chunk
            if len(chunk) != buffer_size:
                break
        return data.decode().strip()

    async def _read_command_(self, reader: StreamReader | None, raw: bool = False):
        """
        Reads a command response from the specified stream reader.

        Args:
            reader (StreamReader | None): The stream reader to read data from.
            raw (bool, optional): Whether to return raw data. Defaults to False.

        Returns:
            Parsed response data or raw data based on the provided flag.
        """
        data = await self._read_(reader)
        if len(data) > 0:
            parsed_data: RESPONSE[T] = json.loads(data)
            if raw:
                return parsed_data

            if not parsed_data["status"]:
                handle_error(parsed_data)
            return parsed_data.get("returnData")
        else:
            return None

    async def _send_command_(
        self,
        writer: StreamWriter | None,
        command: str,
        unauthenticated: bool = False,
        **kwargs: dict[dict],
    ):
        """
        Sends a command to the API.

        Args:
            writer (StreamWriter | None): The stream writer to send data to.
            command (str): The command to send.
            unauthenticated (bool, optional): Whether the command requires authentication. Defaults to False.
            **kwargs: Additional keyword arguments for the command.
        """
        if not unauthenticated and not self._logged_in:
            raise Exception("Not logged in")

        await self._write_(
            writer,
            json.dumps(
                {
                    "command": command,
                    **kwargs,
                }
            ),
        )

    async def _stream_read_(self):
        """
        Reads streaming data from the API and triggers callbacks.

        Continuously reads data from the streaming reader and triggers registered callbacks.
        """
        while True:
            parsed_data = await self._read_command_(self._streaming_reader, raw=True)

            if not parsed_data:
                continue

            command = parsed_data.get("command")
            if not command:
                logging.error(f"Received response: {parsed_data}")
                continue

            callbacks = self._callbacks.get(command)

            if callbacks:
                for callback in callbacks:
                    callback(parsed_data["data"])
            else:
                logging.log(
                    f"Received command: {command} with data: {parsed_data["data"]}"
                )

    async def login(self):
        """
        Authenticate with the XTB API using provided credentials.

        Establishes a connection to the API server and initiates a streaming session.

        Raises:
            Exception: If authentication fails or connection cannot be established.

        Documentation:
            [Login Endpoint](http://developers.xstore.pro/documentation/#login)
        """
        self._reader, self._writer = await asyncio.open_connection(
            self._address, self._connection_info.port, ssl=True
        )

        await self._send_command_(
            self._writer,
            "login",
            unauthenticated=True,
            arguments=dict(userId=self._login, password=self._password),
            appName=self._app_name,
        )
        response: RESPONSE | LOGIN_RESPONSE = await self._read_command_(
            self._reader, raw=True
        )
        if not response["status"]:
            raise Exception(response["errorDescr"])

        self._stream_session_id = response["streamSessionId"]
        (
            self._streaming_reader,
            self._streaming_writer,
        ) = await asyncio.open_connection(
            self._address, self._connection_info.streaming, ssl=True
        )
        self._reading_task = asyncio.Task(self._stream_read_())
        self._logged_in = True
        self._callbacks = defaultdict(list)
        await self.streaming_ping()

    async def logout(self) -> RESPONSE[StreamingTradeStatusRecord]:
        """
        Terminate the authenticated session with the XTB API.

        Closes active connections and cancels any ongoing streaming tasks.

        Returns:
            RESPONSE[StreamingTradeStatusRecord]: Response from the logout command.

        Documentation:
            [Logout Endpoint](http://developers.xstore.pro/documentation/#logout)
        """
        await self._send_command_(self._writer, "logout")
        self._logged_in = False

    async def _send_and_read_command_(
        self, cmd: str, Type: DataClassJsonMixin | None, **kwargs
    ):
        """
        Send a command to the API and read the response.

        Args:
            cmd (str): The command to send.
            Type (DataClassJsonMixin | None): The data class type for parsing the response.
            **kwargs: Additional keyword arguments for the command.

        Returns:
            Parsed response data based on the provided Type.
        """
        await self._send_command_(self._writer, cmd, **kwargs)
        data = await self._read_command_(self._reader)
        if not Type:
            return data

        return (
            Type.from_dict(data)
            if type(data) is not list
            else [Type.from_dict(el) for el in data]
        )

    async def get_all_symbols(self, **kwargs) -> list[SymbolRecord]:
        """
        Retrieve all available trading symbols for the user.

        Args:
            **kwargs: Additional keyword arguments for the command.

        Returns:
            list[SymbolRecord]: A list of symbol records available to the user.

        Documentation:
            [Get All Symbols](http://developers.xstore.pro/documentation/#getAllSymbols)
        """
        return await self._send_and_read_command_(
            "getAllSymbols", SymbolRecord, **kwargs
        )

    async def get_calendar(self, **kwargs) -> list[CalendarRecord]:
        """
        Retrieve market events calendar.

        Args:
            **kwargs: Additional keyword arguments for the command.

        Returns:
            list[CalendarRecord]: A list of calendar records with market events.
        """
        return await self._send_and_read_command_(
            "getCalendar", CalendarRecord, **kwargs
        )

    async def get_chart_last_request(
        self, info: ChartLastInfoRecord, **kwargs
    ) -> ChartResponseRecord:
        """
        Retrieve the latest chart information based on the provided criteria.

        Description:
            Please note that this function can usually be replaced by its streaming equivalent `getCandles`,
            which is the preferred method for retrieving current candle data. Returns chart info from the
            start date to the current time. If the chosen period of `CHART_LAST_INFO_RECORD` is greater
            than 1 minute, the last candle returned by the API can change until the end of the period
            (the candle is automatically updated every minute).

        Limitations:
            - `PERIOD_M1`: <0-1) month
            - `PERIOD_M30`: <1-7) months
            - `PERIOD_H4`: <7-13) months
            - `PERIOD_D1`: 13 months and earlier

            Specific periods are guaranteed within their ranges but may extend slightly beyond.

        Example Scenario:
            - Request charts of 5-minute period for a 3-month time span.
            - Response guarantees 1 month of 5-minute charts.

        Documentation:
            [Get Chart Last Request](http://developers.xstore.pro/documentation/#getChartLastRequest)
        """
        return await self._send_and_read_command_(
            "getChartLastRequest",
            ChartResponseRecord,
            arguments=dict(info=info.to_dict()),
            **kwargs,
        )

    async def get_chart_range_request(
        self, info: ChartRangeInfoRecord, **kwargs
    ) -> ChartResponseRecord:
        """
        Description: Please note that this function can be usually replaced by its streaming equivalent getCandles which is the preferred way of retrieving current candle data. Returns chart info with data between given start and end dates.

        Limitations: there are limitations in charts data availability. Detailed ranges for charts data, what can be accessed with specific period, are as follows:

        PERIOD_M1 --- <0-1) month, i.e. one month time<br />
        PERIOD_M30 --- <1-7) month, six months time<br />
        PERIOD_H4 --- <7-13) month, six months time<br />
        PERIOD_D1 --- 13 month, and earlier on<br />

        Note, that specific PERIOD_ is the lowest (i.e. the most detailed) period, accessible in listed range. For instance, in months range <1-7) you can access periods: PERIOD_M30, PERIOD_H1, PERIOD_H4, PERIOD_D1, PERIOD_W1, PERIOD_MN1. Specific data ranges availability is guaranteed, however those ranges may be wider, e.g.: PERIOD_M1 may be accessible for 1.5 months back from now, where 1.0 months is guaranteed.

        [http://developers.xstore.pro/documentation/#getChartRangeRequest](http://developers.xstore.pro/documentation/#getChartRangeRequest)
        """
        return await self._send_and_read_command_(
            "getChartRangeRequest",
            ChartResponseRecord,
            arguments=dict(info=info.to_dict()),
            **kwargs,
        )

    async def get_commission_def(
        self, symbol: str, volume: float, **kwargs
    ) -> CommissionDefResponseRecord:
        """
        Description: Returns calculation of commission and rate of exchange. The value is calculated as expected value, and therefore might not be perfectly accurate.

        [http://developers.xstore.pro/documentation/#getCommissionDef](http://developers.xstore.pro/documentation/#getCommissionDef)
        """
        return await self._send_and_read_command_(
            "getCommissionDef",
            CommissionDefResponseRecord,
            arguments=dict(symbol=symbol, volume=volume),
            **kwargs,
        )

    async def get_current_user_data(self, **kwargs) -> CurrentUserDataRecord:
        """
        Description: Returns calculation of commission and rate of exchange. The value is calculated as expected value, and therefore might not be perfectly accurate.

        [http://developers.xstore.pro/documentation/#getCurrentUserData](http://developers.xstore.pro/documentation/#getCurrentUserData)
        """
        return await self._send_and_read_command_(
            "getCurrentUserData", CurrentUserDataRecord, **kwargs
        )

    async def get_ibs_history(self, end: Time, start: Time, **kwargs) -> list[IBRecord]:
        """
        Description: Returns IBs data from the given time range.

        [http://developers.xstore.pro/documentation/#getIbsHistory](http://developers.xstore.pro/documentation/#getIbsHistory)
        """
        return await self._send_and_read_command_(
            "getIbsHistory", IBRecord, arguments=dict(end=end, start=start), **kwargs
        )

    async def get_margin_level(self, **kwargs) -> MarginLevelRecord:
        """
        Description: Please note that this function can be usually replaced by its streaming equivalent getBalance which is the preferred way of retrieving account indicators. Returns various account indicators.

        [http://developers.xstore.pro/documentation/#getMarginLevel](http://developers.xstore.pro/documentation/#getMarginLevel)
        """
        return await self._send_and_read_command_(
            "getMarginLevel", MarginLevelRecord, **kwargs
        )

    async def get_margin_trade(
        self, symbol: str, volume: float, **kwargs
    ) -> MarginTradeRecord:
        """
        Description: Returns expected margin for given instrument and volume. The value is calculated as expected margin value, and therefore might not be perfectly accurate.

        [http://developers.xstore.pro/documentation/#getMarginTrade](http://developers.xstore.pro/documentation/#getMarginTrade)
        """
        return await self._send_and_read_command_(
            "getMarginTrade",
            MarginTradeRecord,
            arguments=dict(symbol=symbol, volume=volume),
            **kwargs,
        )

    async def get_news(
        self, start: Time, end: Time = 0, **kwargs
    ) -> list[NewsTopicRecord]:
        """
        Description: Please note that this function can be usually replaced by its streaming equivalent getNews which is the preferred way of retrieving news data. Returns news from trading server which were sent within specified period of time.

        [http://developers.xstore.pro/documentation/#getNews](http://developers.xstore.pro/documentation/#getNews)
        """
        return await self._send_and_read_command_(
            "getNews", NewsTopicRecord, arguments=dict(end=end, start=start), **kwargs
        )

    async def get_profit_calculation(
        self,
        closePrice: float,
        cmd: Command,
        openPrice: float,
        symbol: str,
        volume: float,
        **kwargs,
    ) -> ProfitCalculationRecord:
        """
        Description: Calculates estimated profit for given deal data Should be used for calculator-like apps only. Profit for opened transactions should be taken from server, due to higher precision of server calculation.

        [http://developers.xstore.pro/documentation/#getProfitCalculation](http://developers.xstore.pro/documentation/#getProfitCalculation)
        """
        return await self._send_and_read_command_(
            "getProfitCalculation",
            ProfitCalculationRecord,
            arguments=dict(
                closePrice=closePrice,
                cmd=cmd,
                openPrice=openPrice,
                symbol=symbol,
                volume=volume,
            ),
            **kwargs,
        )

    async def get_server_time(self, **kwargs) -> ServerTimeRecord:
        """
        Description: Returns current time on trading server.

        [http://developers.xstore.pro/documentation/#getServerTime](http://developers.xstore.pro/documentation/#getServerTime)
        """
        return await self._send_and_read_command_(
            "getServerTime", ServerTimeRecord, **kwargs
        )

    async def get_step_rules(self, **kwargs) -> list[StepRuleRecord]:
        """
        Description: Returns a list of step rules for DMAs.

        [http://developers.xstore.pro/documentation/#getStepRules](http://developers.xstore.pro/documentation/#getStepRules)
        """
        return await self._send_and_read_command_(
            "getStepRules", StepRuleRecord, **kwargs
        )

    async def get_symbol(self, symbol: str, **kwargs) -> SymbolRecord:
        """
        Description: Returns information about symbol available for the user.

        [http://developers.xstore.pro/documentation/#getSymbol](http://developers.xstore.pro/documentation/#getSymbol)
        """
        return await self._send_and_read_command_(
            "getSymbol", SymbolRecord, arguments=dict(symbol=symbol), **kwargs
        )

    async def get_tick_prices(
        self, level: int, symbols: list[str], timestamp: Time, **kwargs
    ) -> TickPricesResponseRecord:
        """
        Description: Please note that this function can be usually replaced by its streaming equivalent getTickPrices which is the preferred way of retrieving ticks data. Returns array of current quotations for given symbols, only quotations that changed from given timestamp are returned. New timestamp obtained from output will be used as an argument of the next call of this command.

        [http://developers.xstore.pro/documentation/#getTickPrices](http://developers.xstore.pro/documentation/#getTickPrices)
        """
        return await self._send_and_read_command_(
            "getTickPrices",
            TickPricesResponseRecord,
            arguments=dict(level=level, symbols=symbols, timestamp=timestamp),
            **kwargs,
        )

    async def get_trade_records(self, orders: list[int], **kwargs) -> list[TradeRecord]:
        """
        Description: Returns array of trades listed in orders argument.

        [http://developers.xstore.pro/documentation/#getTradeRecords](http://developers.xstore.pro/documentation/#getTradeRecords)
        """
        return await self._send_and_read_command_(
            "getTradeRecords",
            TradeRecord,
            arguments=dict(orders=orders),
            **kwargs,
        )

    async def get_trades(self, openedOnly: bool, **kwargs) -> list[TradeRecord]:
        """
        Description: Please note that this function can be usually replaced by its streaming equivalent getTrades  which is the preferred way of retrieving trades data. Returns array of user's trades.

        [http://developers.xstore.pro/documentation/#getTrades](http://developers.xstore.pro/documentation/#getTrades)
        """
        return await self._send_and_read_command_(
            "getTrades",
            TradeRecord,
            arguments=dict(openedOnly=openedOnly),
            **kwargs,
        )

    async def get_trades_history(
        self, start: int, end: int = 0, **kwargs
    ) -> list[TradeRecord]:
        """
        Description: Please note that this function can be usually replaced by its streaming equivalent getTrades  which is the preferred way of retrieving trades data. Returns array of user's trades which were closed within specified period of time.

        [http://developers.xstore.pro/documentation/#getTradesHistory](http://developers.xstore.pro/documentation/#getTradesHistory)
        """
        return await self._send_and_read_command_(
            "getTradesHistory",
            TradeRecord,
            arguments=dict(start=start, end=end),
            **kwargs,
        )

    async def get_trading_hours(
        self, symbols: list[str], **kwargs
    ) -> list[TradingHoursRecord]:
        """
        Retrieve trading hours for specified symbols.

        Args:
            symbols (list[str]): List of symbol names to retrieve trading hours for.
            **kwargs: Additional keyword arguments for the command.

        Returns:
            list[TradingHoursRecord]: A list of trading hours records for the specified symbols.
        """
        return await self._send_and_read_command_(
            "getTradingHours",
            TradingHoursRecord,
            arguments=dict(symbols=symbols),
            **kwargs,
        )

    async def get_version(self, **kwargs) -> VersionRecord:
        """
        Retrieve the API version.

        Args:
            **kwargs: Additional keyword arguments for the command.

        Returns:
            VersionRecord: The API version information.
        """
        return await self._send_and_read_command_(
            "getVersion",
            VersionRecord,
            **kwargs,
        )

    async def ping(self, **kwargs) -> None:
        """
        Send a ping to the API to keep the connection alive.

        Args:
            **kwargs: Additional keyword arguments for the command.
        """
        return await self._send_and_read_command_(
            "ping",
            None,
            **kwargs,
        )

    async def trade_transaction(
        self, tradeTransInfo: TradeTransInfoRecord, **kwargs
    ) -> TradeTransResponseRecord:
        """
        Execute a trade transaction.

        Args:
            tradeTransInfo (TradeTransInfoRecord): Information about the trade transaction.
            **kwargs: Additional keyword arguments for the command.

        Returns:
            TradeTransResponseRecord: Response from the trade transaction.
        """
        return await self._send_and_read_command_(
            "tradeTransaction",
            TradeTransResponseRecord,
            arguments=dict(tradeTransInfo=tradeTransInfo.to_dict()),
            **kwargs,
        )

    async def trade_transaction_status(
        self, order: int, **kwargs
    ) -> TradeTransactionStatusResponseRecord:
        """
        Retrieve the status of a trade transaction.

        Args:
            order (int): The order ID to check the status for.
            **kwargs: Additional keyword arguments for the command.

        Returns:
            TradeTransactionStatusResponseRecord: The status of the trade transaction.
        """
        return await self._send_and_read_command_(
            "tradeTransactionStatus",
            TradeTransactionStatusResponseRecord,
            arguments=dict(order=order),
            **kwargs,
        )

    async def _subscribe_(
        self,
        command: str,
        Type: DataClassJsonMixin | None,
        eventListener: Callable[[T], None],
        **kwargs,
    ):
        """
        Subscribe to a specific API command for real-time updates.

        Args:
            command (str): The API command to subscribe to.
            Type (DataClassJsonMixin | None): The data class type for parsing the response.
            eventListener (Callable[[T], None]): The callback function to handle events.
            **kwargs: Additional keyword arguments for the subscription.
        """
        self._callbacks[command].append(
            lambda data: eventListener(Type.from_dict(data)) if Type else eventListener
        )
        await self._send_command_(
            self._streaming_writer,
            f"get{command[0].upper()}{command[1:]}",
            streamSessionId=self._stream_session_id,
            **kwargs,
        )

        async def unsubscribe_fn():
            await self._unsubscribe_(command, **kwargs)

        return unsubscribe_fn

    async def _unsubscribe_(self, command: str, **kwargs):
        """
        Unsubscribe from a specific API command.

        Args:
            command (str): The API command to unsubscribe from.
            **kwargs: Additional keyword arguments for the unsubscription.
        """
        del self._callbacks[command]
        await self._send_command_(
            self._streaming_writer,
            f"stop{command[0].upper()}{command[1:]}",
            streamSessionId=self._stream_session_id,
            **kwargs,
        )

    def subscribe_get_balance(
        self, eventListener: Callable[[StreamingBalanceRecord], None], **kwargs
    ):
        """
        Subscribe to balance updates.

        Args:
            eventListener (Callable[[StreamingBalanceRecord], None]): Callback for balance updates.
            **kwargs: Additional keyword arguments for the subscription.
        """
        return self._subscribe_(
            "balance", StreamingBalanceRecord, eventListener, **kwargs
        )

    def subscribe_get_candles(
        self,
        eventListener: Callable[[StreamingCandleRecord], None],
        symbol: str,
        **kwargs,
    ):
        """
        Subscribe to real-time candle data for a specific symbol.

        Args:
            eventListener (Callable[[StreamingCandleRecord], None]): Callback function to handle candle updates.
            symbol (str): The trading symbol to subscribe to.
            **kwargs: Additional keyword arguments for the subscription.

        Returns:
            Unsubscribe function to terminate the subscription.
        """
        return self._subscribe_(
            "candles", StreamingCandleRecord, eventListener, symbol=symbol, **kwargs
        )

    def subscribe_get_keep_alive(
        self,
        eventListener: Callable[[StreamingKeepAliveRecord], None],
        **kwargs,
    ):
        """
        Description: Subscribes for and unsubscribes from 'keep alive' messages. A new 'keep alive' message is sent by the API every 3 seconds.

        [http://developers.xstore.pro/documentation/#streamgetKeepAlive](http://developers.xstore.pro/documentation/#streamgetKeepAlive)
        """
        return self._subscribe_(
            "keepAlive", StreamingKeepAliveRecord, eventListener, **kwargs
        )

    def subscribe_get_news(
        self, eventListener: Callable[[StreamingNewsRecord], None], **kwargs
    ):
        """
        Description: Subscribes for and unsubscribes from news.

        [http://developers.xstore.pro/documentation/#streamgetNews](http://developers.xstore.pro/documentation/#streamgetNews)
        """
        return self._subscribe_("news", StreamingNewsRecord, eventListener, **kwargs)

    def subscribe_get_profits(
        self, eventListener: Callable[[StreamingProfitRecord], None], **kwargs
    ):
        """
        Description: Subscribes for and unsubscribes from profits.

        [http://developers.xstore.pro/documentation/#streamgetProfits](http://developers.xstore.pro/documentation/#streamgetProfits)
        """
        return self._subscribe_(
            "profits", StreamingProfitRecord, eventListener, **kwargs
        )

    def subscribe_tick_prices(
        self,
        eventListener: Callable[[StreamingTickRecord], None],
        symbol: str,
        minArrivalTime: int = 0,
        maxLevel: int | None = None,
        **kwargs,
    ):
        """
        Description: Establishes subscription for quotations and allows to obtain the relevant information in real-time, as soon as it is available in the system. The getTickPrices  command can be invoked many times for the same symbol, but only one subscription for a given symbol will be created. Please beware that when multiple records are available, the order in which they are received is not guaranteed.

        [http://developers.xstore.pro/documentation/#streamgetTickPrices](http://developers.xstore.pro/documentation/#streamgetTickPrices)
        """
        return self._subscribe_(
            "tickPrices",
            StreamingTickRecord,
            eventListener,
            symbol=symbol,
            minArrivalTime=minArrivalTime,
            maxLevel=maxLevel,
            **kwargs,
        )

    def subscribe_trades(
        self, eventListener: Callable[[StreamingTradeRecord], None], **kwargs
    ):
        """
        Description: Establishes subscription for user trade status data and allows to obtain the relevant information in real-time, as soon as it is available in the system. Please beware that when multiple records are available, the order in which they are received is not guaranteed.

        [http://developers.xstore.pro/documentation/#streamgetTrades](http://developers.xstore.pro/documentation/#streamgetTrades)
        """
        return self._subscribe_("trades", StreamingTradeRecord, eventListener, **kwargs)

    def subscribe_trade_status(
        self, eventListener: Callable[[StreamingTradeStatusRecord], None], **kwargs
    ):
        """
        Description: Allows to get status for sent trade requests in real-time, as soon as it is available in the system. Please beware that when multiple records are available, the order in which they are received is not guaranteed.

        [http://developers.xstore.pro/documentation/#streamgetTradeStatus](http://developers.xstore.pro/documentation/#streamgetTradeStatus)
        """
        return self._subscribe_(
            "tradeStatus", StreamingTradeStatusRecord, eventListener, **kwargs
        )

    async def streaming_ping(self):
        """
        Send a streaming ping to maintain the streaming session.
        """
        await self._send_command_(
            self._streaming_writer, "ping", streamSessionId=self._stream_session_id
        )
