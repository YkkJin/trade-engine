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
        策略Base类
        Params:
        - bus: 事件总线
        - trader: 一个traderspi实例
        - quoter: 一个xmdspi实例
        - log: 策略日志，默认存储在log/name/date路径下
        - id: 策略id
        """

        self.__bus = bus
        self.__trader = trader
        self.__quoter = quoter
        self.__log = self.log_handler()
        self.id = 0
        self.__subscribe_request = None

    def on_tick(self, event: Event):
        pass

    def on_trade(self, event: Event):
        pass

    def on_order(self, event: Event):
        """
        挂单委托监控
        """
        pass

    def on_cancel(self, event: Event):
        """
        撤单回报监听
        """
        pass

    def log_handler(self):
        return DefaultLogHandler(name=self.name, log_type='stdout', filepath='strategy.log')

    def subscribe(self, subscribe_request: SubscribeRequest):
        self.__subscribe_request = subscribe_request
        self.__quoter.subscribe(self.__subscribe_request)

    def unsubscribe(self):
        if not self.__subscribe_request:
            self.__quoter.unsubscribe(self.__subscribe_request)



