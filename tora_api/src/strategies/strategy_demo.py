from math import floor

from ..event.event import Event
from ..event.bus import EventBus
from ..models.model import OrderModel
from ..models.request import LimitPriceBuyRequest, CancelRequest, SubscribeRequest
from ..event.type import EventType
from ..log_handler.default_handler import DefaultLogHandler
from ..tora_stock.traderapi import (
    TORA_TSTP_OST_Accepted,
    TORA_TSTP_EXD_SSE,
    TORA_TSTP_EXD_SZSE,
    TORA_TSTP_EXD_COMM,
    TORA_TSTP_EXD_BSE)
from ..trade import Trader, Quoter
from logging import Logger


class Strategy:
    name = '策略Demo1'

    def __init__(self, bus: EventBus, trader: Trader, quoter: Quoter):
        """
        打板策略
        Params:
        - trader: 一个traderspi实例
        - quoter: 一个xmdspi实例
        - limit_volume: 触发策略封单参数
        - cancel_volume: 触发风控策略撤单参数
        - position: 策略头寸
        """

        self.subscribe_request: SubscribeRequest = None
        self.cancel_req: CancelRequest = None
        self.order_model: OrderModel = None
        self.order_id: str = None #策略执行的委托ID，一个策略同一时刻只产生唯一一个委托

        self.__bus = bus
        self.__trader = trader
        self.__quoter = quoter
        self.log = self.log_handler()


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
        self.log.info(f"{event.payload}")

 

    # 应该是挂单回报监控
    def on_trade(self, event: Event):
        """
        成交回报监听
        检查self__trader是否在OnRtnTrade()中向EventBus实例推送TRADE事件
        """
        if event.payload.OrderID == self.order_id:
            self.log.info("策略触发成交，注销监听函数")
            self.__bus.unregister(EventType.TICK,  self.on_tick)
            self.__bus.unregister(EventType.ORDER, self.on_order)
            self.__bus.unregister(EventType.TRADE, self.on_trade)


    def on_order(self, event: Event):
        """
        挂单委托监控，判断挂单是否成功
        """
        """
        
        
        print("on_order事件监听")
        print(self.__trader.sysid_orderid_map[event.payload.OrderSysID])
        print(self.order_id)
        if self.__trader.sysid_orderid_map[event.payload.OrderSysID] == self.order_id:
            if (event.payload.OrderStatus == TORA_TSTP_OST_Accepted and self.__trader.sysid_orderid_map[
                event.payload.OrderSysID] == self.order_id):
        """
        pass


    def on_cancel(self, event: Event):
        """
        撤单回报监听
        检查self.__trader.OnRspOrderAction()是否在OnRspOrderAction()中向EventBus实例推送CANCEL事件
        """
        pass

    def log_handler(self):
        return DefaultLogHandler(name=self.name, log_type='stdout',filepath='strategy.log')

    def subscribe(self, subscribe_request: SubscribeRequest):
        self.__quoter.subscribe(subscribe_request)
