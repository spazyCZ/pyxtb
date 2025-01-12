import enum
from dataclasses import dataclass
from typing import Literal, TypedDict, TypeVar

from dataclasses_json import CatchAll, Undefined, dataclass_json


T = TypeVar("T")
Time = int

SUCCESS_RESPONSE = TypedDict("SUCCESS_RESPONSE[T]", {"status": True, "returnData": T})
ERROR_RESPONSE = TypedDict(
    "ERROR_RESPONSE[T]", {"status": False, "errorCode": str, "errorDescr": str}
)

RESPONSE = SUCCESS_RESPONSE[T] | ERROR_RESPONSE

LOGIN_RESPONSE = TypedDict("LOGIN_RESPONSE", {"status": True, "streamSessionId": str})


class QuoteId(enum.IntEnum):
    """
    QuoteId enum
    """

    FIXED = 1
    ""
    FLOAT = 2
    ""
    DEPTH = 3
    ""
    CROSS = 4
    ""
    UNKNOWN_1 = 5
    ""
    UNKNOWN_2 = 6
    ""

    def default(self, obj):
        if type(obj) in self.values():
            return obj.value
        raise Exception("Value not in enum")


class MarginMode(enum.IntEnum):
    """
    MarginMode enum
    """

    FOREX = 101
    ""
    CFD_LEVERAGED = 102
    ""
    CFD = 103
    ""
    UNKNOWN = 104
    ""

    def default(self, obj):
        if type(obj) in self.values():
            return obj.value
        raise Exception("Value not in enum")


class ProfitMode(enum.IntEnum):
    """
    ProfitMode enum
    """

    FOREX = 5
    ""
    CFD = 6
    ""

    def default(self, obj):
        if type(obj) in self.values():
            return obj.value
        raise Exception("Value not in enum")


@dataclass_json(
    undefined=Undefined.INCLUDE,
)
@dataclass
class SymbolRecord:
    """
    SYMBOL_RECORD

    [http://developers.xstore.pro/documentation/#SYMBOL_RECORD](http://developers.xstore.pro/documentation/#SYMBOL_RECORD)
    """

    ask: float
    bid: float
    categoryName: str
    contractSize: int
    currency: str
    currencyPair: bool
    currencyProfit: str
    description: str
    expiration: Time | None
    groupName: str
    high: float
    initialMargin: int
    instantMaxVolume: int
    leverage: float
    longOnly: bool
    lotMax: float
    lotMin: float
    lotStep: float
    low: float
    marginHedged: int
    marginHedgedStrong: bool
    marginMaintenance: int | None
    marginMode: MarginMode
    percentage: float
    precision: int
    profitMode: ProfitMode
    quoteId: QuoteId
    shortSelling: bool
    spreadRaw: float
    spreadTable: float
    starting: Time | None
    stepRuleId: int
    stopsLevel: int
    swap_rollover3days: int
    swapEnable: bool
    swapLong: float
    swapShort: float
    swapType: int
    symbol: str
    tickSize: float
    tickValue: float
    time: Time
    timeString: str
    trailingEnabled: bool
    type: int
    _other: CatchAll


@dataclass_json(undefined=Undefined.INCLUDE)
@dataclass
class CalendarRecord:
    """
    CALENDAR_RECORD

    [http://developers.xstore.pro/documentation/#CALENDAR_RECORD](http://developers.xstore.pro/documentation/#CALENDAR_RECORD)
    """

    country: str
    current: str
    forecast: str
    impact: str
    period: str
    previous: str
    time: Time
    title: str
    _other: CatchAll


class Period(enum.IntEnum):
    """
    Period enum
    """

    PERIOD_M1 = 1
    "1 minute"
    PERIOD_M5 = 5
    "5 minutes"
    PERIOD_M15 = 15
    "15 minutes"
    PERIOD_M30 = 30
    "30 minutes"
    PERIOD_H1 = 60
    "60 minutes (1 hour)"
    PERIOD_H4 = 240
    "240 minutes (4 hours)"
    PERIOD_D1 = 1440
    "1440 minutes (1 day)"
    PERIOD_W1 = 10080
    "10080 minutes (1 week)"
    PERIOD_MN1 = 43200
    "43200 minutes (30 days)"

    def default(self, obj):
        if type(obj) in self.values():
            return obj.value
        raise Exception("Value not in enum")


@dataclass_json(undefined=Undefined.INCLUDE)
@dataclass
class ChartLastInfoRecord:
    """
    CHART_LAST_INFO_RECORD

    [http://developers.xstore.pro/documentation/#CHART_LAST_INFO_RECORD](http://developers.xstore.pro/documentation/#CHART_LAST_INFO_RECORD)
    """

    period: Period
    start: Time
    symbol: str
    _other: CatchAll


@dataclass_json(undefined=Undefined.INCLUDE)
@dataclass
class RateInfoRecord:
    """
    RATE_INFO_RECORD

    [http://developers.xstore.pro/documentation/#RATE_INFO_RECORD](http://developers.xstore.pro/documentation/#RATE_INFO_RECORD)
    """

    close: float
    ctm: Time
    ctmString: str
    high: float
    low: float
    open: float
    vol: float
    _other: CatchAll


@dataclass_json(undefined=Undefined.INCLUDE)
@dataclass
class ChartResponseRecord:
    """
    CHART_LAST_INFO_RESPONSE_RECORD
    """

    digits: int
    rateInfos: list[RateInfoRecord]
    _other: CatchAll


@dataclass_json(undefined=Undefined.INCLUDE)
@dataclass
class ChartRangeInfoRecord:
    """
    CHART_RANGE_INFO_RECORD

    [http://developers.xstore.pro/documentation/#CHART_RANGE_INFO_RECORD](http://developers.xstore.pro/documentation/#CHART_RANGE_INFO_RECORD)
    """

    period: Period
    start: Time
    symbol: str
    end: Time
    ticks: int
    _other: CatchAll


@dataclass_json(undefined=Undefined.INCLUDE)
@dataclass
class CommissionDefResponseRecord:
    """
    COMMISSION_DEF_RESPONSE_RECORD
    """

    commission: float
    rateOfExchange: float
    _other: CatchAll


@dataclass_json(undefined=Undefined.INCLUDE)
@dataclass
class CurrentUserDataRecord:
    """
    CURRENT_USER_DATA_RECORD
    """

    companyUnit: int
    currency: str
    group: str
    ibAccount: bool
    leverage: Literal[1]
    leverageMultiplier: float
    spreadType: Literal["FLOAT"] | None
    trailingStop: bool
    _other: CatchAll


@dataclass_json(undefined=Undefined.INCLUDE)
@dataclass
class IBRecord:
    """
    IB_RECORD

    [http://developers.xstore.pro/documentation/#IB_RECORD](http://developers.xstore.pro/documentation/#IB_RECORD)
    """

    close_price: float
    login: str
    nominal: float
    openPrice: float
    side: int
    surname: str
    symbol: str
    timestamp: Time
    volume: float
    _other: CatchAll


@dataclass_json(undefined=Undefined.INCLUDE)
@dataclass
class MarginLevelRecord:
    """
    MARGIN_LEVEL_RECORD
    """

    balance: float
    credit: float
    currency: str
    equity: float
    margin: float
    margin_free: float
    margin_level: float
    _other: CatchAll


@dataclass_json(undefined=Undefined.INCLUDE)
@dataclass
class MarginTradeRecord:
    """
    MARGIN_TRADE_RECORD
    """

    margin: float
    _other: CatchAll


@dataclass_json(undefined=Undefined.INCLUDE)
@dataclass
class NewsTopicRecord:
    """
    NEWS_TOPIC_RECORD

    [http://developers.xstore.pro/documentation/#NEWS_TOPIC_RECORD](http://developers.xstore.pro/documentation/#NEWS_TOPIC_RECORD)
    """

    body: str
    bodylen: int
    key: str
    time: Time
    timeString: str
    title: str
    _other: CatchAll


@dataclass_json(undefined=Undefined.INCLUDE)
@dataclass
class ProfitCalculationRecord:
    """
    PROFIT_CALCULATION_RECORD
    """

    profit: float
    _other: CatchAll


@dataclass_json(undefined=Undefined.INCLUDE)
@dataclass
class ServerTimeRecord:
    """
    SERVER_TIME_RECORD
    """

    time: Time
    timeString: str
    _other: CatchAll


@dataclass_json(undefined=Undefined.INCLUDE)
@dataclass
class StepRecord:
    """
    STEP_RECORD

    [http://developers.xstore.pro/documentation/#STEP_RECORD](http://developers.xstore.pro/documentation/#STEP_RECORD)
    """

    fromValue: float
    step: float
    _other: CatchAll


@dataclass_json(undefined=Undefined.INCLUDE)
@dataclass
class StepRuleRecord:
    """
    STEP_RULE_RECORD

    [http://developers.xstore.pro/documentation/#STEP_RULE_RECORD](http://developers.xstore.pro/documentation/#STEP_RULE_RECORD)
    """

    id: int
    name: str
    steps: list[StepRecord]
    _other: CatchAll


@dataclass_json(undefined=Undefined.INCLUDE)
@dataclass
class TickRecord:
    """
    TICK_RECORD

    [http://developers.xstore.pro/documentation/#TICK_RECORD](http://developers.xstore.pro/documentation/#TICK_RECORD)
    """

    ask: float
    askVolume: int
    bid: float
    bidVolume: int
    high: float
    level: int
    low: float
    spreadRaw: float
    spreadTable: float
    symbol: str
    timestamp: Time
    _other: CatchAll


@dataclass_json(undefined=Undefined.INCLUDE)
@dataclass
class TickPricesResponseRecord:
    """
    TICK_PRICES_RESPONSE_RECORD
    """

    quotations: list[TickRecord]
    _other: CatchAll


class Command(enum.IntEnum):
    """
    Command enum
    """

    BUY = 0
    ""
    SELL = 1
    ""
    BUY_LIMIT = 2
    ""
    SELL_LIMIT = 3
    ""
    BUY_STOP = 4
    ""
    SELL_STOP = 5
    ""
    BALANCE = 6
    "Read only. Used in getTradesHistory for manager's deposit/withdrawal operations (profit>0 for deposit, profit<0 for withdrawal)."
    CREDIT = 7
    "Read only"

    def default(self, obj):
        if type(obj) in self.values():
            return obj.value
        raise Exception("Value not in enum")


@dataclass_json(undefined=Undefined.INCLUDE)
@dataclass
class TradeRecord:
    """
    TRADE_RECORD

    [http://developers.xstore.pro/documentation/#TRADE_RECORD](http://developers.xstore.pro/documentation/#TRADE_RECORD)
    """

    close_price: float
    close_time: Time | None
    close_timeString: str | None
    closed: bool
    cmd: Command
    comment: str
    commission: float
    customComment: str | None
    digits: int
    expiration: Time | None
    expirationString: str | None
    margin_rate: float
    offset: int
    open_price: float
    open_time: Time
    open_timeString: str
    order: int
    order2: int
    position: int
    profit: float | None
    sl: float
    storage: float
    symbol: str
    timestamp: Time
    tp: float
    volume: float
    _other: CatchAll


class Day(enum.IntEnum):
    """
    Day enum
    """

    MONDAY = 1
    ""
    TUESDAY = 2
    ""
    WEDNESDAY = 3
    ""
    THURSDAY = 4
    ""
    FRIDAY = 5
    ""
    SATURDAY = 6
    ""
    SUNDAY = 7
    ""

    def default(self, obj):
        if type(obj) in self.values():
            return obj.value
        raise Exception("Value not in enum")


@dataclass_json(undefined=Undefined.INCLUDE)
@dataclass
class QuotesRecord:
    """
    QUOTES_RECORD

    [http://developers.xstore.pro/documentation/#QUOTES_RECORD](http://developers.xstore.pro/documentation/#QUOTES_RECORD)
    """

    day: Day
    fromT: Time
    toT: Time
    _other: CatchAll


@dataclass_json(undefined=Undefined.INCLUDE)
@dataclass
class TradingRecord:
    """
    TRADING_RECORD

    [http://developers.xstore.pro/documentation/#TRADING_RECORD](http://developers.xstore.pro/documentation/#TRADING_RECORD)
    """

    day: Day
    fromT: Time
    toT: Time
    _other: CatchAll


@dataclass_json(undefined=Undefined.INCLUDE)
@dataclass
class TradingHoursRecord:
    """
    TRADING_HOURS_RECORD

    [http://developers.xstore.pro/documentation/#TRADING_HOURS_RECORD](http://developers.xstore.pro/documentation/#TRADING_HOURS_RECORD)
    """

    quotes: list[QuotesRecord]
    symbol: str
    trading: list[TradingRecord]
    _other: CatchAll


@dataclass_json(undefined=Undefined.INCLUDE)
@dataclass
class VersionRecord:
    """
    VERSION_RECORD

    [http://developers.xstore.pro/documentation/#VERSION_RECORD](http://developers.xstore.pro/documentation/#VERSION_RECORD)
    """

    version: str
    _other: CatchAll


class TransactionType(enum.IntEnum):
    """
    TransactionType enum
    """

    OPEN = 0
    "Order open, used for opening orders"
    PENDING = 1
    "Order pending, only used in the streaming getTrades command"
    CLOSE = 2
    "Order close"
    MODIFY = 3
    "Order modify, only used in the tradeTransaction command"
    DELETE = 4
    "Order delete, only used in the tradeTransaction command"

    def default(self, obj):
        if type(obj) in self.values():
            return obj.value
        raise Exception("Value not in enum")


@dataclass_json(undefined=Undefined.INCLUDE)
@dataclass
class TradeTransInfoRecord:
    """
    TRADE_TRANS_INFO

    [http://developers.xstore.pro/documentation/#TRADE_TRANS_INFO](http://developers.xstore.pro/documentation/#TRADE_TRANS_INFO)
    """

    cmd: Command
    customComment: str | None
    expiration: float
    offset: int
    order: int
    price: float
    sl: float
    symbol: str
    tp: float
    type: TransactionType
    volume: float
    _other: CatchAll


@dataclass_json(undefined=Undefined.INCLUDE)
@dataclass
class TradeTransResponseRecord:
    """
    TRADE_TRANS_RESPONSE_RECORD
    """

    order: int
    _other: CatchAll


class RequestStatus(enum.IntEnum):
    """
    RequestStatus enum
    """

    ERROR = 0
    ""
    PENDING = 1
    ""
    ACCEPTED = 3
    "The transaction has been executed successfully"
    REJECTED = 4
    "The transaction has been rejected"

    def default(self, obj):
        if type(obj) in self.values():
            return obj.value
        raise Exception("Value not in enum")


@dataclass_json(undefined=Undefined.INCLUDE)
@dataclass
class TradeTransactionStatusResponseRecord:
    """
    TRADE_TRANS_STATUS_RESPONSE_RECORD
    """

    ask: float
    bid: float
    customComment: str | None
    message: str | None
    order: int
    requestStatus: RequestStatus
    _other: CatchAll


@dataclass_json(undefined=Undefined.INCLUDE)
@dataclass
class StreamingBalanceRecord:
    """
    STREAMING_BALANCE_RECORD
    """

    balance: float
    credit: float
    equity: float
    margin: float
    marginFree: float
    marginLevel: float
    _other: CatchAll


@dataclass_json(undefined=Undefined.INCLUDE)
@dataclass
class StreamingCandleRecord:
    """
    STREAMING_CANDLE_RECORD
    """

    close: float
    ctm: int
    ctmString: str
    high: float
    low: float
    open: float
    quoteId: QuoteId
    symbol: str
    vol: float
    _other: CatchAll


@dataclass_json(undefined=Undefined.INCLUDE)
@dataclass
class StreamingKeepAliveRecord:
    """
    STREAMING_KEEP_ALIVE_RECORD
    """

    timestamp: int
    _other: CatchAll


@dataclass_json(undefined=Undefined.INCLUDE)
@dataclass
class StreamingNewsRecord:
    """
    STREAMING_NEWS_RECORD
    """

    body: str
    key: str
    time: str
    title: str
    _other: CatchAll


@dataclass_json(undefined=Undefined.INCLUDE)
@dataclass
class StreamingProfitRecord:
    """
    STREAMING_PROFIT_RECORD
    """

    order: int
    order2: int
    position: int
    profit: float
    _other: CatchAll


@dataclass_json(undefined=Undefined.INCLUDE)
@dataclass
class StreamingTickRecord:
    """
    STREAMING_TICK_RECORD
    """

    ask: float
    askVolume: int
    bid: float
    bidVolume: int
    high: float
    level: int
    low: float
    quoteId: QuoteId
    spreadRaw: float
    spreadTable: float
    symbol: str
    timestamp: int
    _other: CatchAll


@dataclass_json(undefined=Undefined.INCLUDE)
@dataclass
class StreamingTradeRecord:
    """
    STREAMING_TRADE_RECORD
    """

    close_price: float
    close_time: int | None
    closed: bool
    cmd: int
    comment: str
    commission: float
    customComment: str | None
    digits: int
    expiration: int | None
    margin_rate: float
    offset: int
    open_price: float
    open_time: int
    order: int
    order2: int
    position: int
    profit: float
    sl: float
    state: str
    storage: float
    symbol: str
    tp: float
    type: int
    volume: float
    _other: CatchAll


@dataclass_json(undefined=Undefined.INCLUDE)
@dataclass
class StreamingTradeStatusRecord:
    """
    STREAMING_TRADE_STATUS_RECORD
    """

    customComment: str | None
    message: str | None
    order: int
    price: float
    requestStatus: int
    _other: CatchAll
