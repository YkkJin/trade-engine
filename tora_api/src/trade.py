from typing import Dict, Tuple, Any, List
from time import sleep
from datetime import datetime

from ..config.config import *
from .models.model import (TickModel,
                           L2TickModel,
                           TradeModel,
                           OrderModel)
from .models.request import OrderRequest, CancelRequest, SubscribeRequest
from .event.bus import EventBus
from .event.event import Event
from .event.type import EventType
from .log_handler.default_handler import DefaultLogHandler
from .tora_stock import (
    traderapi,
    xmdapi,
    lev2mdapi
)

from .tora_stock.traderapi import (
    TORA_TSTP_D_Buy,
    TORA_TSTP_D_Sell,
    TORA_TSTP_EXD_SSE,
    TORA_TSTP_EXD_SZSE,
    TORA_TSTP_EXD_HK,
    TORA_TSTP_EXD_BSE,
    TORA_TSTP_OST_Cached,
    TORA_TSTP_OPT_LimitPrice,
    TORA_TSTP_OPT_FiveLevelPrice,
    TORA_TSTP_OST_AllTraded,
    TORA_TSTP_OST_AllCanceled,
    TORA_TSTP_OST_Accepted,
    TORA_TSTP_OST_PartTradeCanceled,
    TORA_TSTP_OST_PartTraded,
    TORA_TSTP_OST_Rejected,
    TORA_TERT_RESTART,
    TORA_TERT_QUICK,
    TORA_TSTP_LACT_UserID,
    TORA_TSTP_LACT_AccountID,
    TORA_TSTP_PID_SHBond,
    TORA_TSTP_PID_SHFund,
    TORA_TSTP_PID_SHStock,
    TORA_TSTP_PID_SZBond,
    TORA_TSTP_PID_SZFund,
    TORA_TSTP_PID_SZStock,
    TORA_TSTP_PID_BJStock,
    TORA_TSTP_TC_GFD,
    TORA_TSTP_TC_IOC,
    TORA_TSTP_VC_AV,
    TORA_TSTP_AF_Delete,
    CTORATstpQrySecurityField,
    CTORATstpQryInvestorField,
    CTORATstpQryShareholderAccountField,
    CTORATstpQryTradingAccountField,
    CTORATstpQryPositionField,
    CTORATstpQryOrderField,
    CTORATstpQryTradeField,
    CTORATstpInputOrderField,
    CTORATstpInputOrderActionField,
    CTORATstpRspUserLoginField,
    CTORATstpUserLogoutField,

    #
    CTORATstpRspInfoField,
    #
    CTORATstpOrderField,
    CTORATstpConditionOrderField,
    CTORATstpTradeField,
    CTORATstpSecurityField,
    CTORATstpTradingAccountField,
    CTORATstpShareholderAccountField,
    CTORATstpInvestorField,
    CTORATstpPositionField, TORA_TSTP_EXD_COMM,

)
from .tora_stock.xmdapi import (
    CTORATstpMarketDataField,
    CTORATstpSpecificSecurityField
)

EXCHANGE_MAP = {
    0: TORA_TSTP_EXD_COMM,
    1: TORA_TSTP_EXD_SSE,
    2: TORA_TSTP_EXD_SZSE,
    4: TORA_TSTP_EXD_BSE
}

ORDER_STATUS_MAP = {
    0: "预埋",
    1: "未知",
    2: "交易所已接受",
    3: "部分成交",
    4: "全部成交",
    5: "部成部撤",
    6: "全部撤单",
    7: "交易所已拒绝"

}


class L2Quoter(lev2mdapi.CTORATstpLev2MdSpi):
    def __init__(self, bus: EventBus, log: DefaultLogHandler) -> None:
        super().__init__()
        self.bus = bus
        self.log = log

        self.reqid: int = 0
        self.api: lev2mdapi.CTORATstpLev2MdApi_CreateTstpLev2MdApi = None

        self.connect_status: bool = False
        self.login_status: bool = False
        self.subscribed: set = set()

        self.userid: str = ""
        self.password: str = ""
        self.address: str = ""

    def OnFrontConnected(self) -> None:
        """服务器连接成功回报"""
        self.log.info("L2行情服务器链接成功")
        self.login()

    def OnFrontDisconnected(self, reason: int) -> None:
        """服务器连接断开回报"""
        self.login_status = False
        self.log.info(f"L2行情服务器连接断开，原因{reason}")

    def OnRspUserLogin(
            self,
            data: lev2mdapi.CTORATstpRspUserLoginField,
            error: lev2mdapi.CTORATstpRspInfoField,
            reqid: int,
            isLast: bool
    ) -> None:
        """用户登录请求回报"""
        if not error:
           return
        else:
            self.login_status = True
            self.log.info(f"L2行情服务器登录成功",isLast)

    def OnRspSubMarketData(self,
                           data: lev2mdapi.CTORATstpSpecificSecurityField,
                           error: lev2mdapi.CTORATstpRspInfoField,
                           reqid: int,
                           isLast: str):
        if not error:
            return
        else:
            self.log.info("L2行情快照订阅回报", error)

    def OnRspSubNGTSTick(self,
                         data: lev2mdapi.CTORATstpSpecificSecurityField,
                         error: lev2mdapi.CTORATstpRspInfoField,
                         reqid: int,
                         isLast: str):
        if not error:
            return
        else:
            self.log.info("L2股基逐笔委托订阅回报", error)

    def OnRtnMarketData(self, data:lev2mdapi.CTORATstpLev2MarketDataField, FirstLevelBuyNum, FirstLevelBuyOrderVolumes, FirstLevelSellNum, FirstLevelSellOrderVolumes):
        if not data:
            return
        self.log.info(f"{data['SecurityID'],data['DataTimeStamp']},{data['LastPrice']},{data['HighestPrice']},{data['BidPrice1']},{data['BidVolume1']}")

    def OnRtnNGTSTick(self, data: lev2mdapi.CTORATstpLev2NGTSTickField):
        if not data:
            return
        self.log.info(f"{data}")
        L2Tick = L2TickModel(
                ExchangeID=data["ExchangeID"],
                SecurityID=data["SecurityID"],
                MainSeq=data["MainSeq"],
                SubSeq=data["SubSeq"],
                TickTime=data["TickTime"],
                TickType=data["TickType"],
                BuyNo=data["BuyNo"],
                SellNo=data["SellNo"],
                Price=data["Price"],
                Volume=data["Volume"],
                TradeMoney=data["TradeMoney"],
                Side=data["Side"]
            )
        L2TickEvent = Event(
                event_type=EventType.L2TICK,
                payload=L2Tick
            )
        self.log.info("Putting Data")
        self.bus.put(event=L2TickEvent)

    def connect(
            self,
            userid: str,
            password: str,
            address: str,
            account_type: str,
            address_type: str
    ) -> None:
        """连接服务器"""
        self.userid = userid
        self.password = password
        self.address = address
        self.account_type = account_type
        self.address_type = address_type

        # 禁止重复发起连接，会导致异常崩溃
        if not self.connect_status:
            self.api = lev2mdapi.CTORATstpLev2MdApi_CreateTstpLev2MdApi(lev2mdapi.TORA_TSTP_MST_TCP,False)
            self.api.RegisterSpi(self)

            if self.address_type == ADDRESS_FRONT:
                self.api.RegisterFront(address)
            else:
                self.api.RegisterNameServer(address)

            self.api.Init()
            self.log.debug('L2行情API初始化')
            self.connect_status = True

        elif not self.login_status:
            self.log.info("L2行情登录")
            self.login()

    def login(self) -> None:
        login_req: lev2mdapi.CTORATstpReqUserLoginField = lev2mdapi.CTORATstpReqUserLoginField()
        #login_req.LogInAccount = self.userid
        #login_req.Password = self.password
        #login_req.UserProductInfo = "HX5ZJ0C1PV"
        self.reqid += 1
        self.api.ReqUserLogin(login_req, self.reqid)

    def subscribe(self, req: SubscribeRequest) -> None:
        """订阅行情"""
        if self.login_status:
            # exchange: Exchange = EXCHANGE_VT2TORA[req.exchange]
            self.api.SubscribeNGTSTick([str.encode(req.SecurityID)], req.ExchangeID)  # 订阅逐笔委托行情
            self.api.SubscribeMarketData([str.encode(req.SecurityID)], req.ExchangeID)

    def unsubscribe(self, req: SubscribeRequest) -> None:
        if self.login_status:
            self.api.UnSubscribeMarketData([str.encode(req.SecurityID)], req.ExchangeID)

    def logout(self) -> None:
        """关闭连接"""
        if self.connect_status:
            req = lev2mdapi.CTORATstpUserLogoutField()
            req.UserID = self.userid
            self.reqid += 1
            self.api.ReqUserLogout(req, self.reqid)
            self.login_status = False
            self.connect_status = False

    def release(self) -> None:
        self.api.Release()


class Quoter(xmdapi.CTORATstpXMdSpi):
    def __init__(self, bus: EventBus, log: DefaultLogHandler) -> None:
        """构造函数"""
        super().__init__()

        # self.gateway: ToraStockGateway = gateway
        # self.gateway_name: str = gateway.gateway_name
        self.bus = bus
        self.log = log

        self.reqid: int = 0
        self.api: xmdapi.CTORATstpXMdApi_CreateTstpXMdApi = None

        self.connect_status: bool = False
        self.login_status: bool = False
        self.subscribed: set = set()

        self.userid: str = ""
        self.password: str = ""
        self.address: str = ""

        self.current_date: str = datetime.now().strftime("%Y%m%d")

    def OnFrontConnected(self) -> None:
        """服务器连接成功回报"""
        self.log.info("行情服务器链接成功")
        self.login()

    def OnFrontDisconnected(self, reason: int) -> None:
        """服务器连接断开回报"""
        self.login_status = False
        self.log.info(f"行情服务器连接断开，原因{reason}")

    def OnRspUserLogin(
            self,
            data: CTORATstpRspUserLoginField,
            error: CTORATstpRspInfoField,
            reqid: int
    ) -> None:
        """用户登录请求回报"""
        if not error.ErrorID:
            self.login_status = True
            self.log.info("行情服务器登录成功")
        else:
            self.log.info("行情服务器登录失败", error)
            # self.gateway.write_error("行情服务器登录失败", error)

    def OnRspUserLogout(self,
                        data: CTORATstpUserLogoutField,
                        error: CTORATstpRspInfoField,
                        reqid: int) -> None:
        if not error.ErrorID:
            self.login_status = False
            self.log.info("用户退出成功")
        else:
            self.log.info("用户退出失败")

    def OnRspSubMarketData(
            self,
            data: CTORATstpSpecificSecurityField,
            error: CTORATstpRspInfoField,
    ) -> None:
        """订阅行情回报"""
        if not error or not error.ErrorID:
            self.log.info("行情订阅成功")
            return
        self.log.info("行情订阅失败")

    def OnRspUnSubMarketData(
            self,
            data: CTORATstpSpecificSecurityField,
            error: CTORATstpRspInfoField
    ) -> None:
        if not error or not error.ErrorID:
            self.log.info("行情退订成功")
            return

    def OnRtnMarketData(self, data: CTORATstpMarketDataField) -> None:
        """行情数据推送"""
        if not data:
            return
        current_date: str = data.TradingDay
        current_time: str = data.UpdateTime
        # dt: datetime = datetime.strptime(
        # f'{current_date}-{current_time}', "%Y%m%d-%H:%M:%S"
        # )
        # dt: datetime = dt.replace(tzinfo=CHINA_TZ)
        tick = TickModel(
            TradingDay=data.TradingDay,
            UpdateTime=data.UpdateTime,
            SecurityID=data.SecurityID,
            ExchangeID=data.ExchangeID,
            # datetime = dt,
            SecurityName=data.SecurityName,
            Turnover=data.Turnover,
            OpenInterest=data.OpenInterest,
            LastPrice=data.LastPrice,
            Volume=data.Volume,
            UpperLimitPrice=data.UpperLimitPrice,
            LowerLimitPrice=data.LowerLimitPrice,
            OpenPrice=data.OpenPrice,
            HighestPrice=data.HighestPrice,
            LowestPrice=data.LowestPrice,
            PreClosePrice=data.PreClosePrice,
            BidPrice1=data.BidPrice1,
            AskPrice1=data.AskPrice1,
            BidVolume1=data.BidVolume1,
            AskVolume1=data.AskVolume1,
        )

        if data.BidVolume2 or data.AskVolume2:
            tick.BidPrice2 = data.BidPrice2
            tick.BidPrice3 = data.BidPrice3
            tick.BidPrice4 = data.BidPrice4
            tick.BidPrice5 = data.BidPrice5
            tick.AskPrice2 = data.AskPrice2
            tick.AskPrice3 = data.AskPrice3
            tick.AskPrice4 = data.AskPrice4
            tick.AskPrice5 = data.AskPrice5

            tick.BidVolume2 = data.BidVolume2
            tick.BidVolume3 = data.BidVolume3
            tick.BidVolume4 = data.BidVolume4
            tick.BidVolume5 = data.BidVolume5

            tick.AskVolume2 = data.AskVolume2
            tick.AskVolume3 = data.AskVolume3
            tick.AskVolume4 = data.AskVolume4
            tick.AskVolume5 = data.AskVolume5

        self.bus.put(Event(EventType.TICK, tick))

    def connect(
            self,
            userid: str,
            password: str,
            address: str,
            account_type: str,
            address_type: str
    ) -> None:
        """连接服务器"""
        self.userid = userid
        self.password = password
        self.address = address
        self.account_type = account_type
        self.address_type = address_type

        # 禁止重复发起连接，会导致异常崩溃
        if not self.connect_status:
            self.api = xmdapi.CTORATstpXMdApi_CreateTstpXMdApi()
            self.api.RegisterSpi(self)

            if self.address_type == ADDRESS_FRONT:
                self.api.RegisterFront(address)
            else:
                self.api.RegisterNameServer(address)

            self.api.Init()
            self.connect_status = True

        elif not self.login_status:
            self.log.info("行情登录")
            self.login()

    def login(self) -> None:
        """用户登录"""
        login_req: xmdapi.CTORATstpReqUserLoginField = xmdapi.CTORATstpReqUserLoginField()
        login_req.LogInAccount = self.userid
        login_req.Password = self.password
        login_req.UserProductInfo = "HX5ZJ0C1PV"
        self.reqid += 1
        self.api.ReqUserLogin(login_req, self.reqid)

    def subscribe(self, req: SubscribeRequest) -> None:
        """订阅行情"""
        if self.login_status:
            # exchange: Exchange = EXCHANGE_VT2TORA[req.exchange]
            self.api.SubscribeMarketData([str.encode(req.SecurityID)], req.ExchangeID)

    def unsubscribe(self, req: SubscribeRequest) -> None:
        if self.login_status:
            self.api.UnSubscribeMarketData([str.encode(req.SecurityID)], req.ExchangeID)

    def logout(self) -> None:
        """关闭连接"""
        if self.connect_status:
            req = xmdapi.CTORATstpUserLogoutField()
            req.UserID = self.userid
            self.reqid += 1
            self.api.ReqUserLogout(req, self.reqid)

    def release(self) -> None:
        self.api.Release()

    def update_date(self) -> None:
        """更新当前日期"""
        self.current_date: str = datetime.now().strftime("%Y%m%d")


class Trader(traderapi.CTORATstpTraderSpi):

    def __init__(self, bus: EventBus, log: DefaultLogHandler) -> None:
        """构造函数"""
        super().__init__()

        self.bus = bus
        self.log = log

        self.reqid: int = 0
        self.order_ref: int = 0

        self.connect_status: bool = False
        self.login_status: bool = False
        self.auth_status: bool = False
        self.login_failed: bool = False

        self.investor_id: str = None
        self.shareholder_ids: Dict[str, str] = {}
        self.account_id: str = None
        self.localid: int = 10000
        self.api: traderapi.CTORATstpTraderApi.CreateTstpTraderApi = None
        self.userid: str = ""
        self.password: str = ""
        self.frontid: int = 0
        self.sessionid: int = 0

        self.sysid_orderid_map: Dict[str, str] = {}

    def OnFrontConnected(self) -> None:
        """服务器连接成功回报"""
        self.log.info("交易服务器链接成功")
        self.login()

    def OnFrontDisconnected(self, reason: int) -> None:
        """服务器连接断开回报"""
        self.login_status = False
        self.log.info(f"交易服务器链接断开，原因{reason}")

    def OnRspUserLogin(
            self,
            data: CTORATstpRspUserLoginField,
            error: CTORATstpRspInfoField,
            reqid: int,
    ) -> None:
        """用户登录请求回报"""
        if not error.ErrorID:
            self.frontid = data.FrontID
            self.sessionid = data.SessionID
            self.login_status = True
            self.log.info("交易服务器登录成功",error.ErrorID,error.ErrorMsg)
            self.query_contracts()
            self.query_investors()
            self.query_shareholder_ids()
        else:
            self.login_failed = True

            # self.gateway.write_error("交易服务器登录失败", error)
            self.log.info("交易服务器登录失败", error)

    def OnRspUserLogout(
            self,
            data: CTORATstpUserLogoutField,
            error: CTORATstpRspInfoField,
            req: int
    ) -> None:
        if not data:
            return
        if error.ErrorID == -1:
            self.log.info("交易服务器登出失败", error)

    def OnRspOrderAction(
            self,
            data: CTORATstpInputOrderActionField,
            error: CTORATstpRspInfoField,
            reqid: int,
    ) -> None:
        """委托撤单失败回报"""

        if error.ErrorID != 0:
            self.log.info(f"交易撤单失败: {error.ErrorMsg}")
        else:
            self.log.info(f"交易撤单成功，订单编号：{data.FrontID}_{data.SessionID}_{data.OrderRef}")

    def OnRtnOrder(self, data: CTORATstpOrderField) -> None:
        """委托更新推送"""
        '''
        type: OrderType = ORDERTYPE_TORA2VT.get(data.OrderPriceType, None)
        if not type:
            return
        '''
        if not data:
            return
        frontid: int = data.FrontID
        sessionid: int = data.SessionID
        order_ref: int = data.OrderRef
        order_id: str = f"{frontid}_{sessionid}_{order_ref}"

        # timestamp: str = f"{data.InsertDate} {data.InsertTime}"
        # dt: datetime = datetime.strptime(timestamp, "%Y%m%d %H:%M:%S")
        # dt: datetime = dt.replace(tzinfo=CHINA_TZ)

        # print(f"symbol: {symbol}, exchange: {exchange}, order_id: {order_id}")
        order = OrderModel(
            ExchangeID=data.ExchangeID,
            SecurityID=data.SecurityID,
            Direction=data.Direction,
            OrderPriceType=data.OrderPriceType,
            TimeCondition=data.TimeCondition,
            VolumeCondition=data.VolumeCondition,
            LimitPrice=data.LimitPrice,
            VolumeTotalOriginal=data.VolumeTotalOriginal,
            RequestID=data.RequestID,
            FrontID=data.FrontID,
            SessionID=data.SessionID,
            OrderRef=data.OrderRef,
            StatusMsg=data.StatusMsg,
            OrderStatus=data.OrderStatus,
            OrderSysID=data.OrderSysID
        )
        order.OrderID = order_id

        self.sysid_orderid_map[data.OrderSysID] = order.OrderID
        if order.OrderStatus != 0 and order.OrderStatus != 1:  # 不放入未知状态的委托回报
            self.log.info(f"委托成功，订单编号:{order_id}，订单状态：{ORDER_STATUS_MAP[order.OrderStatus]}")
            self.bus.put(Event(event_type=EventType.ORDER, payload=order))

    def OnRspQryOrder(self, data: CTORATstpOrderField, error: CTORATstpRspInfoField, reqid: int, last: bool) -> None:
        if not data:
            return

        order = OrderModel(
            ExchangeID=data.ExchangeID,
            SecurityID=data.SecurityID,
            Direction=data.Direction,
            OrderPriceType=data.OrderPriceType,
            TimeCondition=data.TimeCondition,
            VolumeCondition=data.VolumeCondition,
            LimitPrice=data.LimitPrice,
            VolumeTotalOriginal=data.VolumeTotalOriginal,
            RequestID=data.RequestID,
            FrontID=data.FrontID,
            SessionID=data.SessionID,
            OrderRef=data.OrderRef,
            OrderID=data.OrderID,
            OrderStatus=data.OrderStatus
        )

    def OnRtnTrade(self, data: CTORATstpTradeField) -> None:
        """成交数据推送"""
        if not data:
            return

        symbol: str = data.SecurityID

        '''
        exchange: Exchange = EXCHANGE_TORA2VT[data.ExchangeID]
        '''

        orderid: str = self.sysid_orderid_map[data.OrderSysID]

        timestamp: str = f"{data.TradeDate} {data.TradeTime}"
        dt: datetime = datetime.strptime(timestamp, "%Y%m%d %H:%M:%S")
        # dt: datetime = dt.replace(tzinfo=CHINA_TZ)
        trade: TradeModel = TradeModel(
            SecurityID=data.SecurityID,
            ExchangeID=data.ExchangeID,
            OrderID=data.OrderID,
            TradeID=data.TradeID,
            Direction=data.Direction,
            Price=data.Price,
            Volume=data.Volume
        )
        self.log.info(f"成交数据推送：{trade.model_dump()}")
        self.bus.put(Event(event_type=EventType.TRADE, payload=trade))

    def OnRspQrySecurity(
            self,
            data: CTORATstpSecurityField,
            error: CTORATstpRspInfoField,
            reqid: int,
            last: bool
    ) -> None:
        """合约查询回报"""
        if last:
            self.log.info("合约信息查询成功")
        if not data:
            return
        '''
        contract_data: ContractData = ContractData(
            gateway_name=self.gateway_name,
            symbol=data.SecurityID,
            exchange=EXCHANGE_TORA2VT[data.ExchangeID],
            name=data.SecurityName,
            product=PRODUCT_TORA2VT.get(data.ProductID, Product.EQUITY),
            size=data.VolumeMultiple,
            pricetick=data.PriceTick,
            min_volume=data.MinLimitOrderBuyVolume,
            net_position=True,
        )
        self.gateway.on_contract(contract_data)
        '''

    def OnRspQryTradingAccount(
            self,
            data: CTORATstpTradingAccountField,
            error: CTORATstpRspInfoField,
            reqid: int,
            last: bool
    ) -> None:
        """资金查询回报"""
        if not data:
            return

        self.account_id: str = data.AccountID
        '''
        account_data: AccountData = AccountData(
            gateway_name=self.gateway_name,
            accountid=data.AccountID,
            balance=data.UsefulMoney,
            frozen=data.FrozenCash + data.FrozenCommission
        )
        self.gateway.on_account(account_data)
        '''

    def OnRspQryShareholderAccount(
            self,
            data: CTORATstpShareholderAccountField,
            error: CTORATstpRspInfoField,
            reqid: int,
            last: bool
    ) -> None:
        """客户号查询回报"""
        if not data:
            return

        '''
        exchange: Exchange = EXCHANGE_TORA2VT[data.ExchangeID]
        self.shareholder_ids[exchange] = data.ShareholderID
        '''
        self.shareholder_ids[data.ExchangeID] = data.ShareholderID

    def OnRspQryInvestor(
            self,
            data: CTORATstpInvestorField,
            error: CTORATstpRspInfoField,
            reqid: int,
            last: bool
    ) -> None:
        """用户名查询回报"""
        if not data:
            return
        self.investor_id: str = data.InvestorID

    def OnRspQryPosition(
            self,
            data: CTORATstpPositionField,
            error: CTORATstpRspInfoField,
            reqid: int,
            last: bool
    ) -> None:
        """持仓查询回报"""
        if not data:
            return

        if data.InvestorID != self.investor_id:
            '''
            self.gateway.write_log("OnRspQryPosition:收到其他账户的仓位信息")
            '''
            return

        volume: int = data.CurrentPosition
        if volume == 0:
            price = 0
        else:
            price = data.TotalPosCost / volume

        frozen: int = data.HistoryPosFrozen + data.TodayBSPosFrozen + data.TodayPRPosFrozen
        '''
        position_data: PositionData = PositionData(
            gateway_name=self.gateway_name,
            symbol=data.SecurityID,
            exchange=EXCHANGE_TORA2VT[data.ExchangeID],
            direction=Direction.NET,
            volume=volume,
            frozen=frozen,
            price=price,
            yd_volume=data.HistoryPos,
        )
        self.gateway.on_position(position_data)
        '''

    def OnErrRtnOrderInsert(self, data: CTORATstpInputOrderField, error: CTORATstpRspInfoField, reason: int) -> None:
        """委托下单失败回报"""
        '''
        type: OrderType = ORDERTYPE_TORA2VT.get(data.OrderPriceType, None)
        if not type:
            return
        '''

        order_ref: int = data.OrderRef
        order_id: str = f"{self.frontid}_{self.sessionid}_{order_ref}"
        dt: datetime = datetime.now()
        # dt: datetime = dt.replace(tzinfo=CHINA_TZ)
        '''
        order: OrderData = OrderData(
            symbol=data.SecurityID,
            exchange=EXCHANGE_TORA2VT[data.ExchangeID],
            orderid=order_id,
            type=ORDERTYPE_TORA2VT[data.OrderPriceType],
            direction=DIRECTION_TORA2VT[data.Direction],
            price=data.LimitPrice,
            volume=data.VolumeTotalOriginal,
            status=Status.REJECTED,
            datetime=dt,
            gateway_name=self.gateway_name
        )
        self.gateway.on_order(order)

        self.gateway.write_log(
            f"拒单({order_id}):"
            f"错误码:{error.ErrorID}, 错误消息:{error.ErrorMsg}"
        )
        '''
        self.log.info(
            f"拒单({order_id}): 错误码:{error.ErrorID}, 错误消息:{error.ErrorMsg} , 股票代码:{data.SecurityID}")

    def connect(
            self,
            userid: str,
            password: str,
            address: str,
            account_type: str,
            address_type: str
    ) -> None:
        """连接服务器"""
        self.userid = userid
        self.password = password
        self.address = address
        self.account_type = account_type
        self.address_type = address_type

        if not self.connect_status:
            self.api = traderapi.CTORATstpTraderApi.CreateTstpTraderApi('./flow', False)

            self.api.RegisterSpi(self)

            if self.address_type == ADDRESS_FRONT:
                self.api.RegisterFront(address)
            else:
                self.api.RegisterNameServer(address)
            self.api.SubscribePrivateTopic(TORA_TERT_QUICK)
            self.api.SubscribePublicTopic(TORA_TERT_QUICK)
            self.api.Init()
            self.connect_status = True

    def login(self) -> None:
        """用户登录"""
        login_req: traderapi.CTORATstpReqUserLoginField = traderapi.CTORATstpReqUserLoginField()
        login_req.LogInAccount = self.userid
        login_req.Password = self.password
        login_req.UserProductInfo = "HX5ZJ0C1PV"
        '''login_req.TerminalInfo = get_terminal_info()
        '''
        login_req.TerminalInfo = 'PC;IIP=000.000.000.000;IPORT=00000;LIP=x.xx.xxx.xxx;MAC=123ABC456DEF;HD=XXXXXXXXXX'
        if self.account_type == ACCOUNT_USERID:
            login_req.LogInAccountType = TORA_TSTP_LACT_UserID
        else:
            login_req.LogInAccountType = TORA_TSTP_LACT_AccountID

        self.reqid += 1
        self.api.ReqUserLogin(login_req, self.reqid)

    def logout(self):
        self.reqid += 1
        req = CTORATstpUserLogoutField()
        req.UserID = self.userid
        self.api.ReqUserLogout(req, self.reqid)

    def query_contracts(self, security_id: str = "") -> None:
        """查询合约"""
        req: CTORATstpQrySecurityField = CTORATstpQrySecurityField()
        req.SecurityID = security_id
        self.reqid += 1
        self.api.ReqQrySecurity(req, self.reqid)

    def query_investors(self) -> None:
        """查询用户名"""
        req: CTORATstpQryInvestorField = CTORATstpQryInvestorField()
        self.reqid += 1
        self.api.ReqQryInvestor(req, self.reqid)

    def query_shareholder_ids(self) -> None:
        """查询客户号"""
        req: CTORATstpQryShareholderAccountField = CTORATstpQryShareholderAccountField()
        self.reqid += 1
        self.api.ReqQryShareholderAccount(req, self.reqid)

    def query_accounts(self) -> None:
        """查询资金"""
        req: CTORATstpQryTradingAccountField = CTORATstpQryTradingAccountField()
        self.reqid += 1
        self.api.ReqQryTradingAccount(req, self.reqid)

    def query_positions(self) -> None:
        """查询持仓"""
        req: CTORATstpQryPositionField = CTORATstpQryPositionField()
        self.reqid += 1
        self.api.ReqQryPosition(req, self.reqid)

    def query_orders(self) -> None:
        """查询未成交委托"""
        req: CTORATstpQryOrderField = CTORATstpQryOrderField()
        self.reqid += 1
        self.api.ReqQryOrder(req, self.reqid)

    def query_trades(self) -> None:
        """查询成交"""
        req: CTORATstpQryTradeField = CTORATstpQryTradeField()
        self.reqid += 1
        self.api.ReqQryTrade(req, self.reqid)

    def send_order(self, req: OrderRequest):
        """委托下单"""

        self.reqid += 1
        self.order_ref += 1
        req.ShareholderID = self.shareholder_ids[req.ExchangeID]
        req.OrderRef = self.order_ref

        tora_req: CTORATstpInputOrderField = CTORATstpInputOrderField()
        tora_req.ShareholderID = req.ShareholderID
        tora_req.ExchangeID = EXCHANGE_MAP[int(req.ExchangeID)]
        tora_req.SecurityID = req.SecurityID
        tora_req.OrderPriceType = req.OrderPriceType
        tora_req.Direction = req.Direction
        tora_req.LimitPrice = req.LimitPrice
        tora_req.VolumeTotalOriginal = req.VolumeTotalOriginal
        tora_req.TimeCondition = req.TimeCondition
        tora_req.VolumeCondition = req.VolumeCondition

        self.api.ReqOrderInsert(tora_req, self.reqid)

        order_id: str = f"{self.frontid}_{self.sessionid}_{self.order_ref}"

        '''order: OrderData = req.create_order_data(order_id, self.gateway_name)
        self.gateway.on_order(order)
        '''

        return f"{order_id}"

    def cancel_order(self, req: CancelRequest) -> None:
        """委托撤单"""
        self.reqid += 1
        self.order_ref += 1
        tora_req: CTORATstpInputOrderActionField = CTORATstpInputOrderActionField()
        tora_req.ExchangeID = req.ExchangeID
        tora_req.SecurityID = req.SecurityID
        tora_req.OrderRef = req.OrderRef
        tora_req.FrontID = req.FrontID
        tora_req.SessionID = req.SessionID
        tora_req.ActionFlag = TORA_TSTP_AF_Delete
        tora_req.OrderActionRef = self.order_ref

        self.api.ReqOrderAction(tora_req, self.reqid)

    def release(self):
        self.api.Release()
