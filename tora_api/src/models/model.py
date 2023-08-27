from pydantic import BaseModel


class TickModel(BaseModel):
    TradingDay: str = ""
    UpdateTime: str = ""
    SecurityID: str = ""
    ExchangeID: str = ""
    SecurityName: str = ""
    # datetime: str = ""
    Turnover: float = 0.0
    OpenInterest: float = 0.0
    LastPrice: float = 0.0
    Volume: float = 0.0
    UpperLimitPrice: float = 0.0
    LowerLimitPrice: float = 0.0
    OpenPrice: float = 0.0
    HighestPrice: float = 0.0
    LowestPrice: float = 0.0
    PreClosePrice: float = 0.0
    BidPrice1: float = 0.0
    AskPrice1: float = 0.0
    BidVolume1: float = 0.0
    AskVolume1: float = 0.0

    BidPrice2: float = 0.0
    AskPrice2: float = 0.0
    BidVolume2: float = 0.0
    AskVolume2: float = 0.0

    BidPrice3: float = 0.0
    AskPrice3: float = 0.0
    BidVolume3: float = 0.0
    AskVolume3: float = 0.0

    BidPrice4: float = 0.0
    AskPrice4: float = 0.0
    BidVolume4: float = 0.0
    AskVolume4: float = 0.0

    BidPrice5: float = 0.0
    AskPrice5: float = 0.0
    BidVolume5: float = 0.0
    AskVolume5: float = 0.0


class OrderModel(BaseModel):
    ExchangeID: str = ""
    SecurityID: str = ""
    Direction: str = ""
    OrderPriceType: str = ""
    TimeCondition: str = ""
    VolumeCondition: str = ""
    LimitPrice: float = 0.0
    VolumeTotalOriginal: float = 0.0
    RequestID: int = 0
    FrontID: int = 0
    SessionID: int = 0
    OrderRef: int = 0
    OrderID: str = ""
    OrderStatus: int = 0


class TradeModel(BaseModel):
    SecurityID: str = ""
    ExchangeID: str = ""
    OrderID: str = ""
    TradeID: str = ""
    Direction: str = ""
    Price: float = 0.0
    Volume: int = 0

