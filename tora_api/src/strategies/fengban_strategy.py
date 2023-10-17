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


class Strategy:
    name = '程序化打板策略'

    def __init__(self, bus: EventBus, trader: Trader, quoter: Quoter, limit_volume: int, cancel_volume: int,
                 position: float, count: int, log: DefaultLogHandler, id: int):
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
        self.log = log
        self.id = id

        self.buy_trigger_volume = limit_volume  # 封单量
        self.cancel_trigger_volume = cancel_volume  # 撤封单量
        self.count = count  # 总预设策略执行次数
        self.position = position
        self.cancel_trigger = False
        self.trigger_times = 1  # 执行次数监控


        self.limup_price = self.get_limup_price() # TODO
        self.fengban_volume = 0

    def on_L2OrdTrac(self,event:Event):
        # Transction
        if 'TradePrice' in event.payload.model_dump.keys():
            if event.payload.TradePrice < self.limup_price: # not limup, skip
                return
            else:
                if event.payload.SellNo == 0 and  event.payload.ExecType == 2 and event.payload.ExchangeID == '2': # cancle order (ExchangeID == '2') for SZ (buy only)
                    self.fengban_volume -=  event.payload.TradeVolume


        # Order
        else:
            if event.payload.Price < self.limup_price: # not limup, skip
                return
            else:
                if event.payload.Side == 1 and  event.payload.OrderStatus != "D": # buy order not cancled, add buy volume to fengban_volume
                    self.fengban_volume +=  event.payload.TradeVolume

                elif event.payload.Side == 1 and  event.payload.OrderStatus == "D": # buy order and cancled, subtract volume from fengban
                    self.fengban_volume -=  event.payload.TradeVolume


        ##TODO:  send order if match condition


    def on_L2TICK(self, event: Event):
        # Update the fengban_volume with level2 tick AskVolume1 because
        # order/transaction might be lost during communication
        # L2tick is believed to be always correct
        self.fengban_volume = event.payload.AskVolume1


        ##TODO: send order if match condition

    def execute_cancel(self):
        self.__trader.cancel_order(self.cancel_req)

    # 应该是挂单回报监控
    def on_trade(self, event: Event):
        """
        成交回报监听
        检查self__trader是否在OnRtnTrade()中向EventBus实例推送TRADE事件
        """
        if event.payload.OrderID == self.order_id:
            self.log.info("策略触发成交，注销监听函数")
            self.__bus.unregister(EventType.TICK, self.on_tick)
            self.__bus.unregister(EventType.ORDER, self.on_order)
            self.__bus.unregister(EventType.TRADE, self.on_trade)

        pass

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
        return DefaultLogHandler(name=self.name, log_type='stdout', filepath='strategy.log')

    def subscribe(self, subscribe_request: SubscribeRequest):
        self.subscribe_request = subscribe_request
        self.__quoter.subscribe(self.subscribe_request)

    def unsubscribe(self):
        if not self.subscribe_request:
            self.__quoter.unsubscribe(self.subscribe_request)

    def check_upper_limit(self, event: Event):
        if event.type == EventType.TICK:
            if event.payload.LastPrice == event.payload.UpperLimitPrice \
                    and event.payload.BidPrice1 == event.payload.UpperLimitPrice \
                    and event.payload.BidVolume1 * event.payload.BidPrice1 >= self.buy_trigger_volume:
                return True
        return False

    def check_rm(self, event: Event):
        if event.type == EventType.TICK:
            if event.payload.BidVolume1 * event.payload.BidPrice1 <= self.cancel_trigger_volume:
                return True
        return False