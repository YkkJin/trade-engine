from math import floor
from datetime import datetime
import os

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

from ...config.path import LOG_DIR


class DaBanStrategy:
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
        self.buy_request: LimitPriceBuyRequest = None
        self.order_model: OrderModel = None
        self.order_id: str = None  # 策略执行的委托ID，一个策略同一时刻只产生唯一一个委托

        self.__bus = bus
        self.__trader = trader
        self.__quoter = quoter
        self.log = None
        self.id = id
        self.date = datetime.today().strftime("%Y%m%d")
        os.makedirs(os.path.join(LOG_DIR, self.date), exist_ok=True)

        self.buy_trigger_volume = limit_volume  # 封单量
        self.cancel_trigger_volume = cancel_volume  # 撤封单量
        self.trigger_count = count  # 总预设策略执行次数
        self.position = position
        self.trigger_times = 1  # 执行次数监控
        self.limup_price = None
        self.fengban_volume = 0

    def on_l2OrdTrac(self, event: Event):
        if self.trigger_times > self.trigger_count:
            return
        if event.payload.SecurityID != self.subscribe_request.SecurityID:
            return
        # Transaction
        if 'TradePrice' in event.payload.model_dump().keys():
            if event.payload.TradePrice < self.limup_price:  # not limup, skip
                return
            if event.payload.SellNo == 0 and event.payload.ExecType == 2 and event.payload.ExchangeID == TORA_TSTP_EXD_SZSE:  # cancel order (ExchangeID == '2') for SZ (buy only)
                self.fengban_volume -= event.payload.TradeVolume
                self.log.info(f"on_l2OrdTrac回调触发: 触发类别[逐笔成交] 触发形式[未成交] 当前封板量[{self.fengban_volume}]")
        # Order
        else:
            if event.payload.Price < self.limup_price:  # not limup, skip
                return
            if event.payload.Side == 1 and event.payload.OrderStatus != "D":  # buy order not cancled, add buy volume to fengban_volume
                self.fengban_volume += event.payload.TradeVolume
                self.log.info(f"on_l2OrdTrac回调触发: 触发类别[逐笔委托] 触发形式[挂买单] 当前封板量[{self.fengban_volume}]")
            elif event.payload.Side == 1 and event.payload.OrderStatus == "D":  # buy order and cancled, subtract volume from fengban
                self.fengban_volume -= event.payload.TradeVolume
                self.log.info(f"on_l2OrdTrac回调触发: 触发类别[逐笔委托] 触发形式[撤买单] 当前封板量[{self.fengban_volume}]")
            else:
                return

        self.action()

    def on_l2tick(self, event: Event):
        # Update the fengban_volume with level2 tick AskVolume1 because
        # order/transaction might be lost during communication
        # L2tick is believed to be always correct
        if self.trigger_times > self.trigger_count:
            return
        if event.payload.SecurityID != self.subscribe_request.SecurityID:
            return

        if event.payload.AskPrice1 < self.limup_price:  # not limup, skip
            return
        self.fengban_volume = event.payload.AskVolume1
        self.log.info(f"on_l2Tick回调触发：触发类别[L2快照] 触发形式[买一量] 当前封板量[{self.fengban_volume}]")
        self.action()

    # 应该是挂单回报监控
    def on_trade(self, event: Event):
        """
        成交回报监听
        检查self__trader是否在OnRtnTrade()中向EventBus实例推送TRADE事件
        """
        if event.payload.OrderID == self.order_id:
            self.log.info("策略触发成交，注销监听函数")
            self.__bus.unregister(EventType.TICK, self.on_tick)
            self.__bus.unregister(EventType.L2TICK, self.on_l2tick)
            self.__bus.unregister(EventType.L2OrdTrac, self.on_l2OrdTrac)
            self.__bus.unregister(EventType.ORDER, self.on_order)
            self.__bus.unregister(EventType.TRADE, self.on_trade)

    def on_tick(self):
        pass

    def on_order(self, event: Event):
        """
        挂单委托监控，判断挂单是否成功
        """
        pass

    def on_cancel(self, event: Event):
        """
        撤单回报监听
        """
        pass

    def log_handler(self):
        filepath = os.path.join(LOG_DIR,self.date,f'{self.subscribe_request.SecurityID}.log')
        log_name = f"{self.name}_{self.id}"
        return DefaultLogHandler(name=log_name,log_type='file', filepath=filepath)

    def subscribe(self, subscribe_request: SubscribeRequest):

        self.subscribe_request = subscribe_request
        self.log = self.log_handler()
        self.__quoter.subscribe(self.subscribe_request)
        self.limup_price = self.get_limup_price()
        self.buy_request = self.create_buy_request()
        self.log.info(f"策略订阅成功：证券代码[{self.subscribe_request.SecurityID}] 涨停价[{self.limup_price}]")

    def unsubscribe(self):
        if not self.subscribe_request:
            return
        self.__quoter.unsubscribe(self.subscribe_request)
        self.log.info(f"策略取消订阅成功：{self.subscribe_request.SecurityID}")

    def action(self):
        if self.order_id is None and self.fengban_volume >= self.buy_trigger_volume:  # 如果没有委托，且触发封单参数，则以涨停价挂买入单
            self.log.info(f"策略执行买入委托")
            self.execute_buy()
        if self.order_id is not None and self.fengban_volume <= self.cancel_trigger_volume:  # 如果有委托，且触发撤单参数，则撤单
            self.log.info(f"策略执行撤单委托")
            self.execute_cancel()

    def execute_cancel(self):
        self.__trader.cancel_order(self.cancel_req)
        self.log.info(f"策略撤单成功")

    def execute_buy(self):
        self.order_id = self.__trader.send_order(self.buy_request)
        self.log.info(f"策略委托买入成功")
        self.cancel_req = self.buy_request.create_cancel_order_request(self.__trader.order_ref)  # 生成撤单委托

    def create_buy_request(self):
        req = LimitPriceBuyRequest()
        req.ExchangeID = self.subscribe_request.ExchangeID
        req.SecurityID = self.subscribe_request.SecurityID
        req.LimitPrice = self.limup_price
        req.VolumeTotalOriginal = floor(int(self.position / self.limup_price) / 100) * 100  # 改成100的整数倍
        return req

    def check_buy(self):
        '''
        判断是否触发买入条件：
        条件1. 看当前fengban_volume是否大于预设的buy_trigger_volume
        '''
        if self.fengban_volume >= self.buy_trigger_volume:
            return True
        return False

    def check_cancel(self):
        if self.fengban_volume <= self.cancel_trigger_volume:
            return True
        return False

    def get_limup_price(self):
        return self.__trader.contract_limup_price[self.subscribe_request.SecurityID]
