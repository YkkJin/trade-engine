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


class StrategyBase:
    name = 'base'

    def __init__(self, bus: EventBus, trader: Trader, quoter: Quoter):
        """
        打板策略
        Params:
        - trader: 一个traderspi实例
        - quoter: 一个xmdspi实例
        - limit_volume: 触发策略封单参数
        - cancel_volume: 触发风控策略撤单参数
        - position: 策略头寸
        - count: 风控撤单触发次数
        """

        self.subscribe_request: SubscribeRequest = None
        self.cancel_req: CancelRequest = None
        self.order_model: OrderModel = None
        self.order_id: str = None  # 策略执行的委托ID，一个策略同一时刻只产生唯一一个委托

        self.__bus = bus
        self.__trader = trader
        self.__quoter = quoter
        self.log = self.log_handler()
        self.id = id

    def on_tick(self, event: Event):
        self.log.info(event.payload)


    # 应该是挂单回报监控
    def on_trade(self, event: Event):
        pass

    def on_order(self, event: Event):
        """
        挂单委托监控，判断挂单是否成功
        """
        pass

    def on_cancel(self, event: Event):
        """
        撤单回报监听
        检查self.__trader.OnRspOrderAction()是否在OnRspOrderAction()中向EventBus实例推送CANCEL事件
        """
        pass

    def log_handler(self):
        return DefaultLogHandler(name=self.name, log_type='stdout', filepath='strategy.log')

    def subscribe(self, subscribe_request: SubscribeRequest):
        self.subscribe_request = subscribe_request
        self.__quoter.subscribe(self.subscribe_request)

    def unsubscribe(self):
        if not self.subscribe_request:
            self.__quoter.unsubscribe(self.subscribe_request)



