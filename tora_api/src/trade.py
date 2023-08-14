from typing import Dict,Tuple,Any,List
from ..src.tora_stock import traderapi as traderapi
from ..config.config import *
from time import sleep
from datetime import datetime
from ..src.tora_stock.traderapi import (
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
    
    #CTORATstpSpecificSecurityField,
    CTORATstpRspInfoField,
    #CTORATstpMarketDataField,
    CTORATstpOrderField,
    CTORATstpConditionOrderField,
    CTORATstpTradeField,
    CTORATstpSecurityField,
    CTORATstpTradingAccountField,
    CTORATstpShareholderAccountField,
    CTORATstpInvestorField,
    CTORATstpPositionField,
    
)

class Trader(traderapi.CTORATstpTraderSpi):
    

    def __init__(self) -> None:
        """构造函数"""
        super().__init__()


        self.reqid: int = 0
        self.order_ref: int = 0

        self.connect_status: bool = False
        self.login_status: bool = False
        self.auth_status: bool = False
        self.login_failed: bool = False

        self.investor_id: str = None
        self.shareholder_ids: Dict[Exchange, str] = {}
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
        #self.gateway.write_log("交易服务器连接成功")
        self.login()

    def OnFrontDisconnected(self, reason: int) -> None:
        """服务器连接断开回报"""
        self.login_status = False
        print("交易服务器链接断开:{reason}")
       #self.gateway.write_log(f"交易服务器连接断开，原因{reason}")

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
            #self.gateway.write_log("交易服务器登录成功")
            print("交易服务器登录成功")

            self.query_contracts()
            self.query_investors()
            self.query_shareholder_ids()
        else:
            self.login_failed = True

            #self.gateway.write_error("交易服务器登录失败", error)

            print("交易服务器登录失败",error)
        
    def OnRspUserLogout(
        self,
        data: CTORATstpUserLogoutField,
        error: CTORATstpRspInfoField,
        req: int
    ) -> None:
        if not data:
            return 
        if error.ErrorID == -1:
            print(error.ErrorMsg)
        print(error.ErrorID)
        print(error.ErrorMsg)
        print("User {data.UserID} logout successfully")
        
        

    def OnRspOrderAction(
        self,
        data: CTORATstpInputOrderActionField,
        error: CTORATstpRspInfoField,
        reqid: int,
    ) -> None:
        """委托撤单失败回报"""
        error_id: int = error.ErrorID
        if error_id:
            raise ValueError("交易撤单失败")
            print("交易撤单失败", error)
        print("交易撤单成功")
        print(f"order_id: {data.FrontID}_{data.SessionID}_{data.OrderRef}")
        

    def OnRtnOrder(self, data: CTORATstpOrderField) -> None:
        """委托更新推送"""
        '''
        type: OrderType = ORDERTYPE_TORA2VT.get(data.OrderPriceType, None)
        if not type:
            return
        '''
        if not data:
            print("无委托")
            return
        symbol: str = data.SecurityID
        #exchange: Exchange = EXCHANGE_TORA2VT[data.ExchangeID]
        exchange: str = data.ExchangeID
        frontid: int = data.FrontID
        sessionid: int = data.SessionID
        order_ref: int = data.OrderRef
        order_id: str = f"{frontid}_{sessionid}_{order_ref}"

        #timestamp: str = f"{data.InsertDate} {data.InsertTime}"
        #dt: datetime = datetime.strptime(timestamp, "%Y%m%d %H:%M:%S")
        #dt: datetime = dt.replace(tzinfo=CHINA_TZ)
        print("委托更新推送")
        print(f"symbol: {symbol}, exchange: {exchange}, order_id: {order_id}")
        '''
        order: OrderData = OrderData(
            symbol=symbol,
            exchange=exchange,
            orderid=order_id,
            type=ORDERTYPE_TORA2VT[data.OrderPriceType],
            direction=DIRECTION_TORA2VT[data.Direction],
            price=data.LimitPrice,
            volume=data.VolumeTotalOriginal,
            traded=data.VolumeTraded,
            status=ORDER_STATUS_TORA2VT[data.OrderStatus],
            datetime=dt,
            gateway_name=self.gateway_name
        )
        self.gateway.on_order(order)
        '''

        self.sysid_orderid_map[data.OrderSysID] = order_id
    
    def OnRspQryOrder(self, data: CTORATstpOrderField, error: CTORATstpRspInfoField, reqid: int, last: bool) -> None: 
        if not data:
            return 
        
        order_id = data.OrderLocalID
        front_id = data.FrontID
        session_id = data.SessionID 
        price_type = data.OrderPriceType
        ref = data.OrderRef
        security = data.SecurityID 
        direction = data.Direction
        insert_date = data.InsertDate
        insert_time = data.InsertTime

        print(f"date:{insert_date}, time: {insert_time}, order_id: {front_id}_{session_id}_{ref}, security: {security}, direction: {direction}, price_type: {price_type},  price: {data.LimitPrice}, OrderStatus: {data.OrderStatus}, StatusMsg: {data.StatusMsg}, VolumeTraded: {data.VolumeTraded}, VolumeCanceled: {data.VolumeCanceled}")



    def OnRtnTrade(self, data: CTORATstpTradeField) -> None:
        if not data:
            return
        """成交数据推送"""
        symbol: str = data.SecurityID

        '''
        exchange: Exchange = EXCHANGE_TORA2VT[data.ExchangeID]
        '''

        orderid: str = self.sysid_orderid_map[data.OrderSysID]

        timestamp: str = f"{data.TradeDate} {data.TradeTime}"
        dt: datetime = datetime.strptime(timestamp, "%Y%m%d %H:%M:%S")
        #dt: datetime = dt.replace(tzinfo=CHINA_TZ)
        '''
        trade: TradeData = TradeData(
            symbol=symbol,
            exchange=exchange,
            orderid=orderid,
            tradeid=data.TradeID,
            direction=DIRECTION_TORA2VT[data.Direction],
            price=data.Price,
            volume=data.Volume,
            datetime=dt,
            gateway_name=self.gateway_name
        )
        self.gateway.on_trade(trade)
        '''
        print("成交数据推送")
        print(symbol,data.ExchangeID,orderid,data.TradeID,data.Direction,data.Price,data.Volume)

    def OnRspQrySecurity(
        self,
        data: CTORATstpSecurityField,
        error: CTORATstpRspInfoField,
        reqid: int,
        last: bool
    ) -> None:
        """合约查询回报"""
        if last:
            '''self.gateway.write_log("合约信息查询成功")'''
            print("合约信息查询成功")
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
        print(f"name: {data.SecurityName}, size: {data.VolumeMultiple}, pricetick: {data.PriceTick}")



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
        print("资金回报查询")
        print(f"accountid: {data.AccountID}, balance: {data.UsefulMoney}, fronze: {data.FrozenCash}")

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
        print("客户号查询")
        print(f"Exchange: {data.ExchangeID}, ShareholderID:{data.ShareholderID}")
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
        print(f"InvestorID: {data.InvestorID}")

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
            print("OnRspQryPosition:收到其他账户的仓位信息")
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
        print("持仓查询")
        print(f"symbol: {data.SecurityID},exchange: {data.ExchangeID},name: {data.SecurityName} ,volume: {volume}, price: {price}, 股份可用: {data.AvailablePosition}")
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
        #dt: datetime = dt.replace(tzinfo=CHINA_TZ)
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
        print (f"委托下单失败回报: 拒单({order_id}): 错误码:{error.ErrorID}, 错误消息:{error.ErrorMsg} , symbol:{data.SecurityID},volume:{data.VolumeTotalOriginal}")
        

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
            self.api = traderapi.CTORATstpTraderApi.CreateTstpTraderApi('./flow',False)

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
        self.api.ReqUserLogout(req,self.reqid)

    def query_contracts(self,security_id:str = "600000") -> None:
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

    def send_order(self, req: CTORATstpInputOrderField):
        """委托下单"""

        '''
        if req.type not in ORDER_TYPE_VT2TORA:
            self.gateway.write_log(f"委托失败，不支持的委托类型{req.type.value}")
            return ""
        '''

        self.reqid += 1
        self.order_ref += 1

        #req.ShareholderID = self.shareholder_ids[req.ExchangeID]
        req.OrderRef = self.order_ref
        '''

        opt, tc, vc = ORDER_TYPE_VT2TORA[req.type]

        info: CTORATstpInputOrderField = CTORATstpInputOrderField()
        info.ShareholderID = self.shareholder_ids[req.exchange]
        info.SecurityID = req.symbol
        info.ExchangeID = EXCHANGE_VT2TORA[req.exchange]
        info.OrderRef .order_ref
        info.OrderPriceType = self= opt
        info.Direction = DIRECTION_VT2TORA[req.direction]
        info.LimitPrice = req.price
        info.VolumeTotalOriginal = int(req.volume)
        info.TimeCondition = tc
        info.VolumeCondition = vc
        '''

        self.api.ReqOrderInsert(req, self.reqid)

        order_id: str = f"{self.frontid}_{self.sessionid}_{self.order_ref}"
       
        '''order: OrderData = req.create_order_data(order_id, self.gateway_name)
        self.gateway.on_order(order)
        '''

        return f"{order_id}"
    
    def send_cond_order(self,req:CTORATstpConditionOrderField) -> None: 
        """委托条件单 """
        pass

    def cancel_order(self, req: CTORATstpInputOrderActionField) -> None:
        """委托撤单"""
        self.reqid += 1
        self.order_ref += 1
        '''
        info: CTORATstnputOrderActionField = CTORATstpInputOrderActiopInField()
        info.ExchangeID = EXCHANGE_VT2TORA[req.exchange]
        info.SecurityID = req.symbol

        frontid, sessionid, order_ref = req.orderid.split("_")
        info.OrderRef = int(order_ref)
        info.FrontID = int(frontid)
        info.SessionID = int(sessionid)
        info.ActionFlag = TORA_TSTP_AF_Delete
        info.OrderActionRef = self.order_ref
    '''
        req.ActionFlag = TORA_TSTP_AF_Delete
        req.OrderActionRef = self.order_ref
        self.api.ReqOrderAction(req, self.reqid)
    def release(self):
        self.api.Release()


if __name__ == "__main__":
    from config.config import UserID,Password,FrontAddress
    from tora_stock.test_order import (
        LimitPriceOrderReq,
        LimitPriceOrderReqSell,
        FiveLevelPriceToCancelOrderReq,
        FiveLevelPriceToCancelOrderReqSell,
        FiveLevelPriceToLimitOrderReq,
        FiveLevelPriceToLimitOrderReqSell,
        HomeBestPriceOrderReq,
        HomeBestPriceOrderReqSell,
        BestPriceOrderReq,
        BestPriceOrderReqSell
    )
    trader = Trader()
    trader.connect(UserID,Password,FrontAddress['level1_trade'],ACCOUNT_USERID,ADDRESS_FRONT)
    sleep(1)
    trader.query_accounts()
    sleep(1)
    trader.query_orders()
    sleep(1)
    trader.query_positions()
    sleep(1)
    LimitPriceReqOrderID = trader.send_order(LimitPriceOrderReq)
    FiveLevelPriceToCancelOrderReqOrderID = trader.send_order(FiveLevelPriceToCancelOrderReq)
    FiveLevelPriceToLimitOrderReqOrderID = trader.send_order(FiveLevelPriceToLimitOrderReq)
    HomeBestPriceOrderReqOrderID = trader.send_order(HomeBestPriceOrderReq)
    bestPriceOrderReqOrderID = trader.send_order(BestPriceOrderReq)



   


    input() 

    trader.release()


