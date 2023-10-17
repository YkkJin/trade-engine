from pydantic import BaseModel




class SecurityFieldModel(BaseModel):
    TradingDay: str = ""
    ExchangeID: str = ""
    SecurityID: str = ""
    SecurityName: str = ""
    UpperLimitPrice: float = 0.0
    LowerLimitPrice: float = 0.0



class TickModel(BaseModel):
    '''
    L1行情快照
    '''
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


class L2TickModel(BaseModel):
    '''
    L2行情快照
    '''
    SecurityID: str = ""
    ExchangeID: str = ""
    DataTimeStamp: str = ""
    LastPrice: float = 0.0
    UpperLimitPrice: float = 0.0
    LowerLimitPrice: float = 0.0
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

    BidPrice6 : float = 0.0
    AskPrice6 : float = 0.0
    BidVolume6: float = 0.0
    AskVolume6: float = 0.0

    BidPrice7: float = 0.0
    AskPrice7: float = 0.0
    BidVolume7: float = 0.0
    AskVolume7: float = 0.0

    BidPrice8: float = 0.0
    AskPrice8: float = 0.0
    BidVolume8: float = 0.0
    AskVolume8: float = 0.0

    BidPrice9: float = 0.0
    AskPrice9: float = 0.0
    BidVolume9: float = 0.0
    AskVolume9: float = 0.0

    BidPrice10: float = 0.0
    AskPrice10: float = 0.0
    BidVolume10: float = 0.0
    AskVolume10: float = 0.0

    WithdrawBuyNumber: float = 0.0
    WithdrawBuyAmount: float = 0.0
    WithdrawBuyMoney: float = 0.0
    WithdrawSellNumber: float = 0.0
    WithdrawSellAmount: float = 0.0
    WithdrawSellMoney: float = 0.0

class Lev2OrderDetailModel(BaseModel):
    ExchangeID: str = ""
    SecurityID: str = ""
    OrderTime: str = ""
    Price: float = 0.0
    Volume: int = 0
    Side: str = ""
    OrderType: str = ""
    MainSeq: str = ""
    Subseq: str = ""
    OrderNo: str = ""
    OrderStatus: str = ""


class Lev2TransactionDetailModel(BaseModel):
    ExchangeID: str = ""
    SecurityID: str = ""
    TradeTime: str = ""
    TradePrice: float = 0.0
    TradeVolume: int = 0
    ExecType: str = ""
    MainSeq: str = ""
    SubSeq: str = ""
    BuyNo: str = ""
    SellNo: str = ""







class OrderModel(BaseModel):
    '''
    委托
    '''
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
    StatusMsg: str = ""
    OrderSysID: str = ""


class TradeModel(BaseModel):
    '''
    成交
    '''
    SecurityID: str = ""
    ExchangeID: str = ""
    OrderID: str = ""
    TradeID: str = ""
    Direction: str = ""
    Price: float = 0.0
    Volume: int = 0

