from typing import Dict, Tuple, Any, List
from time import sleep
from datetime import datetime
import psutil
from collections import defaultdict

from ..config.tora import *
from .models.model import (TickModel,
                           SecurityFieldModel,
                           L2TickModel,
                           TradeModel,
                           OrderModel,
                           Lev2OrderDetailModel,
                           Lev2TransactionDetailModel)
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
    CTORATstpConnectionInfoField,
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
            self.log.info(f"L2行情服务器登录成功", isLast)

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
            self.log.info("L2股基逐笔委托订阅回报", error["ErrorMsg"])

    def OnRtnOrderDetail(self, data: lev2mdapi.CTORATstpLev2OrderDetailField):
        if not data:
            return
        l2ord = Lev2OrderDetailModel()
        l2ord.SecurityID = data["SecurityID"]
        l2ord.ExchangeID = data["ExchangeID"].decode()
        l2ord.Price = data["Price"]
        l2ord.Volume = data["Volume"]
        l2ord.Side = data["Side"].decode()
        l2ord.OrderStatus = data["OrderStatus"].decode()
        l2ord.MainSeq = data["MainSeq"]
        l2ord.SubSeq = data["SubSeq"]
        #self.log.info(f"逐笔委托推送: 委托时间[{data['OrderTime']}] 证券代码[{data['SecurityID']}] 交易所[{data['ExchangeID'].decode()}] 委托价格[{data['Price']}] 委托成交量[{data['Volume']}] 方向[{data['Side'].decode()}] 委托状态[{data['OrderStatus'].decode()}] 主序列号[{data['MainSeq']}] 子序列号[{data['SubSeq']}]")
        self.bus.put(Event(EventType.L2OrdTrac, l2ord))

    def OnRtnTransaction(self, data: lev2mdapi.CTORATstpLev2TransactionField):
        if not data:
            return
        l2transac = Lev2TransactionDetailModel()
        l2transac.SecurityID = data["SecurityID"]
        l2transac.ExchangeID = data["ExchangeID"].decode()
        l2transac.TradeTime = data["TradeTime"]
        l2transac.TradePrice = data["TradePrice"]
        l2transac.TradeVolume = data["TradeVolume"]
        l2transac.ExecType = data["ExecType"].decode()
        l2transac.MainSeq = int(data["MainSeq"])
        l2transac.SubSeq = int(data["SubSeq"])
        l2transac.BuyNo = int(data["BuyNo"])
        l2transac.SellNo = int(data["SellNo"])
        #self.log.info(f"逐笔成交推送: 成交时间[{data['TradeTime']}] 证券代码[{data['SecurityID']}] 交易所[{data['ExchangeID'].decode()}] 委托价格[{data['TradePrice']}] 委托成交量[{data['TradeVolume']}] 成交类型[{data['ExecType'].decode()}] 主序列号[{data['MainSeq']}] 子序列号[{data['SubSeq']}] 买方代码[{data['BuyNo']}]  卖方代码[{data['SellNo']}]")
        self.bus.put(Event(EventType.L2OrdTrac, l2transac))

    def OnRtnMarketData(self, data: lev2mdapi.CTORATstpLev2MarketDataField, FirstLevelBuyNum, FirstLevelBuyOrderVolumes,
                        FirstLevelSellNum, FirstLevelSellOrderVolumes):
        if not data:
            return
        l2tick = L2TickModel()
        l2tick.SecurityID = data["SecurityID"]
        l2tick.ExchangeID = data["ExchangeID"]
        l2tick.DataTimeStamp = data["DataTimeStamp"]
        l2tick.LastPrice = data["LastPrice"]
        l2tick.UpperLimitPrice = data["UpperLimitPrice"]
        l2tick.LowerLimitPrice = data["LowerLimitPrice"]
        l2tick.HighestPrice = data["HighestPrice"]
        l2tick.LowestPrice = data["LowestPrice"]
        l2tick.PreClosePrice = data["PreClosePrice"]
        l2tick.BidPrice1 = data["BidPrice1"]
        l2tick.AskPrice1 = data["AskPrice1"]
        l2tick.BidVolume1 = data["BidVolume1"]
        l2tick.AskVolume1 = data["AskVolume1"]
        l2tick.BidPrice2 = data["BidPrice2"]
        l2tick.AskPrice2 = data["AskPrice2"]
        l2tick.BidVolume2 = data["BidVolume2"]
        l2tick.AskVolume2 = data["AskVolume2"]
        l2tick.BidPrice3 = data["BidPrice3"]
        l2tick.AskPrice3 = data["AskPrice3"]
        l2tick.BidVolume3 = data["BidVolume3"]
        l2tick.AskVolume3 = data["AskVolume3"]
        l2tick.BidPrice4 = data["BidPrice4"]
        l2tick.AskPrice4 = data["AskPrice4"]
        l2tick.BidVolume4 = data["BidVolume4"]
        l2tick.AskVolume4 = data["AskVolume4"]
        l2tick.BidPrice5 = data["BidPrice5"]
        l2tick.AskPrice5 = data["AskPrice5"]
        l2tick.BidVolume5 = data["BidVolume5"]
        l2tick.AskVolume5 = data["AskVolume5"]
        l2tick.BidPrice6 = data["BidPrice6"]
        l2tick.AskPrice6 = data["AskPrice6"]
        l2tick.BidVolume6 = data["BidVolume6"]
        l2tick.AskVolume6 = data["AskVolume6"]
        l2tick.BidPrice7 = data["BidPrice7"]
        l2tick.AskPrice7 = data["AskPrice7"]
        l2tick.BidVolume7 = data["BidVolume7"]
        l2tick.AskVolume7 = data["AskVolume7"]
        l2tick.BidPrice8 = data["BidPrice8"]
        l2tick.AskPrice8 = data["AskPrice8"]
        l2tick.BidVolume8 = data["BidVolume8"]
        l2tick.AskVolume8 = data["AskVolume8"]
        l2tick.BidPrice9 = data["BidPrice9"]
        l2tick.BidVolume9 = data["BidVolume9"]
        l2tick.AskPrice9 = data["AskPrice9"]
        l2tick.AskVolume9 = data["AskVolume9"]

        l2tick.BidPrice10 = data["BidPrice10"]
        l2tick.AskPrice10 = data["AskPrice10"]
        l2tick.BidVolume10 = data["BidVolume10"]
        l2tick.AskVolume10 = data["AskVolume10"]
        """
        l2tick.WithdrawBuyNumber = data.WithdrawBuyNumber
        l2tick.WithdrawBuyAmount = data.WithdrawBuyAmount
        l2tick.WithdrawBuyMoney = data.WithdrawBuyMoney
        l2tick.WithdrawSellNumber = data.WithdrawSellNumber
        l2tick.WithdrawSellAmount = data.WithdrawSellAmount
        l2tick.WithdrawSellMoney = data.WithdrawSellMoney
        """
        self.bus.put(Event(EventType.L2TICK, l2tick))
        #self.log.info(f"L2行情快照 快照时间[{data['DataTimeStamp']}] 证券代码[{data['SecurityID']}] 交易所[{data['ExchangeID'].decode()}] 现价[{data['LastPrice']}] 买一价[{data['BidPrice1']}] 买一量[{data['BidVolume1']}]")

    def OnRtnNGTSTick(self, data: lev2mdapi.CTORATstpLev2NGTSTickField):
        if not data:
            return
        print("OnRtnNGTSTick SecurityID[%s] TickTime[%s] TickType[%s] Price[%s] Volume[%s]" % (
            data["SecurityID"],
            data['TickTime'],
            data["TickType"],
            data["Price"],
            data["Volume"]
        ))

    def connect(
            self,
            userid: str,
            password: str
    ) -> None:
        """连接服务器"""
        self.userid = userid
        self.password = password

        # 禁止重复发起连接，会导致异常崩溃
        if not self.connect_status:
            self.api = lev2mdapi.CTORATstpLev2MdApi_CreateTstpLev2MdApi(lev2mdapi.TORA_TSTP_MST_MCAST, True)
            self.api.RegisterSpi(self)

            self.api.RegisterMulticast("udp://224.224.2.2:7889","172.16.2121.1","")

            self.api.Init()
            self.log.debug('L2行情API初始化')
            self.connect_status = True

        elif not self.login_status:
            self.log.info("L2行情登录")
            self.login()

    def login(self) -> None:
        login_req: lev2mdapi.CTORATstpReqUserLoginField = lev2mdapi.CTORATstpReqUserLoginField()
        login_req.LogInAccount = self.userid
        login_req.Password = self.password
        login_req.UserProductInfo = "HX5ZJ0C1PV"
        self.reqid += 1
        self.api.ReqUserLogin(login_req, self.reqid)

    def subscribe(self, req: SubscribeRequest) -> None:
        """订阅行情"""
        if self.login_status:
            self.api.SubscribeOrderDetail([str.encode(req.SecurityID)], req.ExchangeID)  # 订阅逐笔委托
            self.api.SubscribeTransaction([str.encode(req.SecurityID)], req.ExchangeID)  # 订阅逐笔成交
            self.api.SubscribeMarketData([str.encode(req.SecurityID)], req.ExchangeID)  # 订阅L2行情快照

    def unsubscribe(self, req: SubscribeRequest) -> None:
        if self.login_status:
            self.api.UnSubscribeMarketData([str.encode(req.SecurityID)], req.ExchangeID)
            self.api.UnSubscribeTransaction([str.encode(req.SecurityID)], req.ExchangeID)
            self.api.UnSubscribeOrderDetail([str.encode(req.SecurityID)], req.ExchangeID)

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
        self.terminal_info = f'PC;IIP=NA;IPORT=NA;LIP=NA;MAC=123ABC456DEF;HD=00b6f88d0890cb7c2b505cb50cb00506;@HX5ZJ0C1PV'

        self.investor_id: str = None
        self.shareholder_ids: Dict[str, str] = {}
        self.account_id: str = None
        self.localid: int = 10000
        self.api: traderapi.CTORATstpTraderApi = None
        self.userid: str = ""
        self.password: str = ""
        self.frontid: int = 0
        self.sessionid: int = 0

        self.sysid_orderid_map: Dict[str, str] = {}
        self.process = psutil.Process()

        self.contract_limup_price = defaultdict()

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
            self.log.info("交易服务器登录成功")
            self.query_contracts()
            self.query_investors()
            self.query_shareholder_ids()
        else:
            self.login_failed = True

            # self.gateway.write_error("交易服务器登录失败", error)
            self.log.info(f"交易服务器登录失败，原因:{error.ErrorMsg}")

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
        if not data:
            return
        order = OrderModel()
        order.OrderID = self.sysid_orderid_map[data.OrderSysID]
        #order.SecurityID = data.SecurityID
        #order.ExchangeID = data.ExchangeID
        order.SInfo = data.SInfo
        order.IInfo = data.IInfo
        error_id = error.ErrorID
        error_msg = error.ErrorMsg
        if error_id == 0:
            self.log.info(f"撤单成功，{order.OrderID},{error_msg}")
            self.bus.put(Event(event_type=EventType.CANCEL_SUCCESS, payload=order))  
            #self.bus.put(Event(event_type=EventType.ORDER_SUCCESS, payload=order))
        else:
            order.OrderStatus = error.ErrorID 
            order.StatusMsg = error.ErrorMsg
            self.log.info(f"撤单失败，{order.OrderID},{error_msg}")
            self.bus.put(Event(event_type=EventType.CANCEL_ERROR, payload=order)) 
         
            

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
            StatusMsg = data.StatusMsg,
            OrderStatus=data.OrderStatus,
            OrderSysID=data.OrderSysID,
            IInfo=data.IInfo,
            SInfo=data.SInfo
        )
        order.OrderID = order_id

        self.sysid_orderid_map[data.OrderSysID] = order.OrderID
        if order.OrderStatus != 0 and order.OrderStatus != 1:  # 不放入未知状态的委托回报
            #self.log.info(f"委托成功，订单编号:{order_id}，订单状态：{ORDER_STATUS_MAP[order.OrderStatus]}")
            self.bus.put(Event(event_type=EventType.ORDER_SUCCESS, payload=order))

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
            OrderSysID=data.OrderSysID,
            OrderStatus=data.OrderStatus,
            IInfo=data.IInfo,
            SInfo=data.SInfo
        )

    def OnRtnTrade(self, data: CTORATstpTradeField) -> None:
        """成交数据推送"""
        if not data:
            return

        symbol: str = data.SecurityID
        order_id: str = self.sysid_orderid_map[data.OrderSysID]
        #timestamp: str = f"{data.TradeDate} {data.TradeTime}"
        #dt: datetime = datetime.strptime(timestamp, "%Y%m%d %H:%M:%S")
        # dt: datetime = dt.replace(tzinfo=CHINA_TZ)
        trade: TradeModel = TradeModel(
            SecurityID=data.SecurityID,
            ExchangeID=data.ExchangeID,
            OrderSysID = data.OrderSysID,
            TradeID=data.TradeID,
            Direction=data.Direction,
            Price=data.Price,
            Volume=data.Volume,
            TradeDate = data.TradeDate,
            TradeTime = data.TradeTime,
        )
        trade.OrderID = order_id
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
        self.contract_limup_price[data.SecurityID] = data.UpperLimitPrice
        security = SecurityFieldModel()
        security.TradingDay = data.TradingDay
        security.ExchangeID = data.ExchangeID
        security.SecurityName = data.SecurityName
        security.UpperLimitPrice = data.UpperLimitPrice
        security.LowerLimitPrice = data.LowerLimitPrice 



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
    
    def OnRspGetConnectionInfo(self, data: CTORATstpConnectionInfoField, error: CTORATstpRspInfoField, req_id: int) -> None:
        self.log.info(f'PC;IIP={data.InnerIPAddress};IPORT={data.InnerPort};LIP={data.OuterIPAddress};MAC={data.MacAddress};HD=00b6f88d0890cb7c2b505cb50cb00506;@HX5ZJ0C1PV')
        self.terminal_info = f'PC;IIP=NA;IPORT=NA;LIP={data.OuterIPAddress};MAC={data.MacAddress};HD=00b6f88d0890cb7c2b505cb50cb00506;@HX5ZJ0C1PV'


    def OnErrRtnOrderInsert(self, data: CTORATstpInputOrderField, error: CTORATstpRspInfoField, reason: int) -> None:
        """委托下单失败回报"""
        if data == None:
            return
        #self.log.info(f"{type(data.Direction)}")
        order_ref: int = data.OrderRef
        order_id: str = f"{self.frontid}_{self.sessionid}_{order_ref}"
        dt: datetime = datetime.now()
        order = OrderModel()
        order.SecurityID = data.SecurityID
        order.ExchangeID = data.ExchangeID
        order.LimitPrice = data.LimitPrice
        order.VolumeTotalOriginal = data.VolumeTotalOriginal
        order.Direction = data.Direction
        order.Status = "REJECTED"
        order.StatusMsg = error.ErrorMsg
        order.IInfo = data.IInfo
        order.SInfo = data.SInfo 
        #order.OrderID = order_id
        #self.log.info(f"created order model")
        self.bus.put(Event(event_type=EventType.ORDER_ERROR, payload=order))


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
            self.api = traderapi.CTORATstpTraderApi_CreateTstpTraderApi('./flow', False,traderapi.TORA_TSTP_TCM_PROXY)

            self.api.RegisterSpi(self)

            if self.address_type == ADDRESS_FRONT:
                self.api.RegisterFront(address)
            else:
                self.api.RegisterNameServer(address)
            self.api.SubscribePrivateTopic(TORA_TERT_QUICK)
            self.api.SubscribePublicTopic(TORA_TERT_QUICK)
            self.api.Init()
            self.connect_status = True
            self.get_connection_info()
            

    def login(self) -> None:
        """用户登录"""
        login_req: traderapi.CTORATstpReqUserLoginField = traderapi.CTORATstpReqUserLoginField()
        login_req.LogInAccount = self.userid
        login_req.Password = self.password
        login_req.UserProductInfo = "HX5ZJ0C1PV"
        '''login_req.TerminalInfo = get_terminal_info()
        '''
        login_req.TerminalInfo = self.terminal_info
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

    def send_order(self, req: OrderRequest) -> None:
        """委托下单"""

        self.reqid += 1
        self.order_ref += 1
        req.ShareholderID = self.shareholder_ids[req.ExchangeID]
        req.OrderRef = self.order_ref #报单引用选填

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
        tora_req.SInfo = req.SInfo
        tora_req.IInfo = req.IInfo

        self.api.ReqOrderInsert(tora_req, self.reqid)

        


    def get_connection_info(self) -> None:
        self.reqid += 1
        self.api.ReqGetConnectionInfo(self.reqid)

    def cancel_order(self, req: CancelRequest) -> None:
        """委托撤单"""
        self.reqid += 1
        # 使用OrderSysID撤单
        tora_req: CTORATstpInputOrderActionField = CTORATstpInputOrderActionField()
        tora_req.ExchangeID = req.ExchangeID
        tora_req.OrderSysID = req.OrderSysID
        tora_req.ActionFlag = TORA_TSTP_AF_Delete
        tora_req.SInfo = req.SInfo
        tora_req.IInfo = req.IInfo
        self.api.ReqOrderAction(tora_req, self.reqid)

    def release(self):
        self.api.Release()

    def set_affinity(self):
        self.process.cpu_affinity([49])
        self.log.info(f"交易绑定核心: {self.process.cpu_affinity()}")