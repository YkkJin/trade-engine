from ..event.event import Event
from ..models.model import OrderModel
from ..models.request import LimitPriceBuyRequest, CancelRequest, SubscribeRequest
from ..event.type import EventType
from ..tora_stock.traderapi import (
    TORA_TSTP_OST_Accepted,
    TORA_TSTP_EXD_SSE,
    TORA_TSTP_EXD_SZSE,
    TORA_TSTP_EXD_COMM,
    TORA_TSTP_EXD_BSE)
from ..trade import Trader, Quoter
from logging import Logger




class Strategy:
    def __init__(self, trader: Trader, quoter: Quoter, limit_volume: int, cancel_volume: int, position: float):

        self.name = 'test'
        self.subscribe_request: SubscribeRequest = None
        self.cancel_req: CancelRequest = None
        self.order_model: OrderModel = None
        self.order_id: str = None

        self.__trader = trader
        self.__quoter = quoter

        self.buy_trigger_volume = limit_volume
        self.cancel_trigger_volume = cancel_volume
        self.position = position
        self.cancel_trigger = False

    def on_tick(self, event: Event):
        """
        监听Tick事件，同时打包盘中跟板策略以及撤单风控
        模块1：check_upper_limit()
            1. 判断当前Tick事件是否满足涨停条件
            2. 判断涨停是否触发跟板策略
        模块2：execute_follow()
            1. 根据参数执行买入
            2. 记录挂单OrderID
            3. 返回CancelReq实例
            4. 开启策略挂单回报监控 -> 监控 挂单时间 以及 买一量
        模块3：execute_cancel()
            1. 判断cancel_trigger状态
            2. 根据参数执行撤单风控
            3. 开启撤单回报监听
        """
        # if self.check_upper_limit(event) and not self.cancel_trigger:
        # execute_follow() 逻辑
        # check_upper_limit做两层判断，第一层判断个股是否涨停，第二层判断是否触发涨停跟板封单参数设定
        # cancel_trigger判断之前是否触发成交后建立撤单风控逻辑
        # 如果触发涨停，则以买一价、封单金额、封单量（股）执行买入
        req = LimitPriceBuyRequest()
        req.ExchangeID = event.payload.ExchangeID
        req.SecurityID = event.payload.SecurityID
        req.LimitPrice = event.payload.BidPrice1
        req.VolumeTotalOriginal = int(self.position / event.payload.BidPrice1) # 得改成100的整数倍
        self.order_id = self.__trader.send_order(req)
        req.OrderID = self.order_id

        # 根据买入委托生成撤单委托
        cancel_req = req.create_cancel_order_request(self.__trader.order_ref)
        self.cancel_req = cancel_req

        if self.cancel_trigger:
            # 是否触发成交回报监听以及是否触发撤单风控
            self.execute_cancel()
            # 撤单风控重置
            self.cancel_trigger = False

    def execute_cancel(self):
        self.__trader.cancel_order(self.cancel_req)

    # 应该是挂单回报监控
    def on_trade(self, event: Event):
        """
        成交回报监听
        检查self__trader.OnRtnTrade()是否在OnTrade中向EventBus实例推送TRADE事件
        """

        pass
        """
        if event.type != EventType.TRADE:
            return
        if self.cancel_trigger:
            # 已经触发过撤单风控
            return
        front_id, session_id, order_ref = self.order_id.split("_")
        if event.payload.FrontID == front_id and \
                event.payload.SessionID == session_id and \
                event.payload.OrderRef == order_ref:
            self.cancel_trigger = True
        """

    def on_order(self, event: Event):
        """
        挂单委托监控，判断挂单是否成功，并根据挂单时长执行撤单
        """
        if event.payload.OrderStatus == TORA_TSTP_OST_Accepted:
            self.cancel_trigger = True

    def on_cancel(self, event: Event):
        """
        撤单回报监听
        检查self.__trader.OnRspOrderAction()是否在OnCancel中向EventBus实例推送CANCEL事件
        """
        pass

    def subscribe(self, subscribe_request: SubscribeRequest):
        self.__quoter.subscribe(subscribe_request)

    def check_upper_limit(self, event: Event):
        if event.type == EventType.TICK:
            if event.payload.LastPrice == event.payload.UpperLimitPrice \
                    and event.payload.BidPrice1 == event.payload.UpperLimitPrice \
                    and event.payload.BidVolume1 >= self.buy_trigger_volume:
                return True
        return False

    def check_rm(self, event: Event):
        if event.type == EventType.TICK:
            if event.payload.BidVolume1 <= self.cancel_trigger_volume:
                return True
        return False
