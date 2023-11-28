from math import floor
from datetime import datetime
import os

from ..event.event import Event
from ..event.engine import EventEngine
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


RUNNING = 0
ORDER_SENT = 1
ORDER_CANCELED = 2
TRADED = 3
STOPPED = 4
ORDER_CANCELED_ABNORMAL = 5
REJECTED = -1


EXCHANGE_MAPPING_TORA2ST = {
    TORA_TSTP_EXD_SSE: 'SSE',
    TORA_TSTP_EXD_SZSE: 'SZSE'
}




class DaBanStrategy:
    name = '程序化打板策略'
    def __init__(self, engine: EventEngine, trader: Trader, quoter: Quoter, limit_volume: int, cancel_volume: int,
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
        self.order: OrderModel = None
        self.order_id: str = None  # 策略执行的委托ID，一个策略同一时刻只产生唯一一个委托

        self.__engine = engine
        self.__trader = trader
        self.__quoter = quoter
        self.log = None
        self.id = id
        self.date = datetime.today().strftime("%Y%m%d")
        self.status = RUNNING
        

        self.buy_trigger_volume = limit_volume  # 封单量
        self.cancel_trigger_volume = cancel_volume  # 撤封单量
        self.trigger_count = count  # 总预设策略执行次数
        self.position = position
        self.trigger_times = 0  # 执行次数监控
        self.limup_price = None
        self.order_error_tolerance = 0
        self.fengban_volume = 0
        self.if_sent_order = False
        self.if_sent_cancel = False

        os.makedirs(os.path.join(LOG_DIR, self.date), exist_ok=True)

    def on_l2OrdTrac(self, event: Event):
        if event.payload.SecurityID != self.subscribe_request.SecurityID:
            return
        self.status = RUNNING
        # Transaction
        if 'TradePrice' in event.payload.model_dump().keys() and self.subscribe_request.ExchangeID == TORA_TSTP_EXD_SZSE: # 如果为深市行情，则依据成交判断委托
            if event.payload.TradePrice < self.limup_price:  # not limup, skip
                self.log.info(f"on_l2OrdTrac回调触发：触发类别[逐笔成交] 触发结果[成交价小于涨停价] {event.payload.SellNo} type[{type(event.payload.SellNo)}] {event.payload.ExecType} type[{type(event.payload.ExecType)}]")
                return
            #self.log.info(f"on_l2OrdTrac回调触发：触发类别[逐笔成交] 触发结果[成交价等于涨停价] {event.payload.SellNo} type[{type(event.payload.SellNo)}] {event.payload.ExecType} type[{type(event.payload.ExecType)}]")
            if event.payload.TradePrice == self.limup_price and event.payload.SellNo == 0 and event.payload.ExecType == "2":  # cancel order (ExchangeID == '2') for SZ (buy only)
                self.fengban_volume -= event.payload.TradeVolume
                self.log.info(f"on_l2OrdTrac回调触发: 触发类别[逐笔成交] 触发形式[未成交] 当前封板量[{self.fengban_volume}]")
                self.action()
                return
        # Order
        if 'TradePrice' not in event.payload.model_dump().keys():
            if event.payload.Price < self.limup_price:  # not limup, skip
                #self.log.info(f"on_l2OrdTrac回调触发：触发类别[逐笔委托] 触发结果[委托价小于涨停价]")
                return
            if event.payload.Price == self.limup_price and event.payload.Side == "1" and event.payload.OrderStatus != "D":  # buy order not cancled, add buy volume to fengban_volume
                payload_volume = event.payload.Volume
    
                self.fengban_volume += payload_volume
                self.log.info(f"on_l2OrdTrac回调触发: 触发类别[逐笔委托] 触发形式[挂买单] 当前封板量[{self.fengban_volume}]")
                self.action()
                return
            if event.payload.Price == self.limup_price and event.payload.Side == "1" and event.payload.OrderStatus == "D":  # buy order and cancled, subtract volume from fengban
                payload_volume = event.payload.Volume

                self.fengban_volume -= payload_volume
                self.log.info(f"on_l2OrdTrac回调触发: 触发类别[逐笔委托] 触发形式[撤买单] 当前封板量[{self.fengban_volume}]")
                self.action()
                return

        #self.action()

    def on_l2tick(self, event: Event):
        # Update the fengban_volume with level2 tick AskVolume1 because
        # order/transaction might be lost during communication
        # L2tick is believed to be always correct        
        self.status = RUNNING
        if event.payload.SecurityID != self.subscribe_request.SecurityID:
            return
        payload_b1_volume = event.payload.BidVolume1
        self.log.info(f"on_l2Tick回调触发：触发类别[L2快照] 触发形式[行情接收] 买一价[{event.payload.BidPrice1}] 买一量[{payload_b1_volume}]") 
        if event.payload.BidPrice1 < self.limup_price:  # not limup, skip
            return
        self.fengban_volume = payload_b1_volume
        self.log.info(f"on_l2Tick回调触发：触发类别[L2快照] 触发形式[买一量] 当前封板量[{self.fengban_volume}]")
        self.action()


    def log_handler(self):
        filepath = os.path.join(LOG_DIR,self.date,f'{self.subscribe_request.SecurityID}{EXCHANGE_MAPPING_TORA2ST[self.subscribe_request.ExchangeID]}_{self.id}_{datetime.today().strftime("%H%M%S")}.log')
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
        # 只要trader有过一次send_order，就不执行买入，防止on_order事件被on_tick或on_l2ordTrac挤兑。
        if self.if_sent_order == False and self.fengban_volume*self.limup_price >= self.buy_trigger_volume: 
            self.log.info(f"策略执行买入委托")
            self.execute_buy()
            return
        # 确认on_order回报成功后再执行撤单，if_sent_cancel防止过度发送撤单请求
        if self.order is not None and self.if_sent_cancel == False and self.fengban_volume*self.limup_price <= self.cancel_trigger_volume:  
            self.log.info(f"策略执行撤单委托")
            self.execute_cancel()
            return

    def execute_cancel(self):
        if self.cancel_req is not None:
            self.__trader.cancel_order(self.cancel_req)
            self.if_sent_cancel = True
        return
            
    def execute_buy(self):
        self.__trader.send_order(self.buy_request)
        self.if_sent_order = True
        return

    def create_buy_request(self):
        req = LimitPriceBuyRequest()
        req.ExchangeID = self.subscribe_request.ExchangeID
        req.SecurityID = self.subscribe_request.SecurityID
        req.LimitPrice = self.limup_price
        req.VolumeTotalOriginal = (int(self.position / self.limup_price) // 100) * 100  # 改成100的整数倍
        
        #===== 通过SInfo和IInfo来唯一确定委托归属 =====##
        req.SInfo = f"{self.id}"   # SInfo标记委托策略归属 
        req.IInfo = self.trigger_times # IInfo标记委托策略触发归属
        return req

    def create_cancel_request(self):
        req = CancelRequest()
        req.ExchangeID = self.order.ExchangeID
        req.SecurityID = self.order.SecurityID
        req.OrderSysID = self.order.OrderSysID
        req.SInfo = f"{self.id}"
        req.IInfo = self.trigger_times
        self.log.info(f"创建撤单委托: 股票代码[{req.SecurityID}] 交易所[{req.ExchangeID}] 委托编号[{self.order.OrderID}] 系统报单编号[{self.order.OrderSysID}] 归属策略编号[{self.order.SInfo}] 归属策略执行次数[{self.order.IInfo}]")
        return req


    def get_limup_price(self):
        return self.__trader.contract_limup_price[self.subscribe_request.SecurityID]


    def on_order(self, event: Event):
        """
        委托回报监听
        """
        if event.payload.SecurityID != self.subscribe_request.SecurityID:
            return 
        if event.payload.SInfo != f"{self.id}" and event.payload.IInfo != self.trigger_times: # 
            self.log.info(f"on_order回调触发 状态[委托归属不一致] 回报委托归属策略ID[{event.payload.SInfo}] 当前策略ID[{self.id}] 回报委托归属策略执行次数[{event.payload.IInfo}] 当前策略执行次数[{self.trigger_times}]")
            return
            
        if event.type == EventType.ORDER_SUCCESS:
            self.log.info(f"on_order回调触发 状态[委托成功] 委托价格[{event.payload.LimitPrice}] 委托股数[{event.payload.VolumeTotalOriginal}] 委托报单编号：{event.payload.OrderSysID}")
            self.status = ORDER_SENT
            self.order = OrderModel()
            self.order.ExchangeID = event.payload.ExchangeID
            self.order.SecurityID = event.payload.SecurityID
            self.order.Direction = event.payload.Direction
            self.order.OrderPriceType = event.payload.OrderPriceType 
            self.order.TimeCondition = event.payload.TimeCondition
            self.order.VolumeCondition = event.payload.VolumeCondition
            self.order.RequestID = event.payload.RequestID
            self.order.FrontID = event.payload.FrontID
            self.order.SessionID = event.payload.SessionID 
            self.order.OrderRef = event.payload.OrderRef 
            self.order.OrderID = event.payload.OrderID 
            self.order.OrderStatus = event.payload.OrderStatus
            self.order.StatusMsg = event.payload.StatusMsg 
            self.order.OrderSysID = event.payload.OrderSysID
            self.order.SInfo = event.payload.SInfo
            self.order.IInfo = event.payload.IInfo
            # 委托成功后创建撤单委托
            self.cancel_req = self.create_cancel_request()
            return 
        if event.type == EventType.ORDER_ERROR:
            self.log.info(f"on_order回调触发 状态[委托失败] 原因[{event.payload.StatusMsg}] 委托价格[{event.payload.LimitPrice}] 委托股数[{event.payload.VolumeTotalOriginal}] 委托编号：{event.payload.OrderID} ")
            self.order_id = None
            self.order = None
            self.cancel_req = None
            self.if_sent_cancel = False 
            self.if_sent_order = False
            self.status = REJECTED
            
            if self.order_error_tolerance > 2:
                self.log.info(f"on_order回调触发 状态[委托失败上限] 请检查失败原因")
                self.status = STOPPED
                self.stop()
            self.order_error_tolerance += 1    
            return

    def on_cancel(self, event: Event):
        """
        撤单回报监听
        
        Note:
            - InputOrderActionField没有OrderID字段，因此只能用SInfo和IInfo来判断
        """
        #self.log.info("on_cancel回调触发 判断SecurityID前触发")
        if self.order is None:
            return

        if event.payload.OrderSysID != self.order.OrderSysID:
            return
        if event.payload.SInfo != f"{self.id}" and event.payload.IInfo != self.trigger_times:
            self.log.info(f"on_cancel回调触发 状态[委托归属不一致] 回报委托归属策略ID[{event.payload.SInfo}] 当前策略ID[{self.id}] 回报委托策略执行次数[{event.payload.IInfo}] 当前策略执行次数[{self.trigger_times}]")
            return
        #self.log.info("on_cancel回调触发 判断撤单成功触发")
        if event.type == EventType.CANCEL_SUCCESS:
            self.log.info(f"on_cancel回调触发 状态[撤单成功] 委托编号[{event.payload.OrderID}] 状态消息[{event.payload.StatusMsg}]")
            self.order_id = None
            self.cancel_req = None
            self.order = None
            self.status = ORDER_CANCELED
            self.buy_request = None
            self.trigger_times += 1
            
            if self.trigger_times >= self.trigger_count:
                self.log.info("策略触发达到上限，策略停止")
                self.status = STOPPED
                self.stop()
                return

            self.buy_request = self.create_buy_request()
            return 
        if event.type == EventType.CANCEL_ERROR:
            self.status = ORDER_CANCELED_ABNORMAL
            self.log.info(f"on_cancel回调触发 状态[撤单失败] 委托编号[{event.payload.OrderID}] 状态消息[{event.payload.StatusMsg}]")
            return 
    
    def on_trade(self, event: Event):
        """
        成交回报监听
        """
        if event.payload.SecurityID != self.subscribe_request.SecurityID:
            return 
        if event.payload.OrderSysID != self.order.OrderSysID:
            self.log.info(f"on_trade回调触发 状态[系统报单不一致] 系统报单编号[{event.payload.OrderID}] 策略绑定报单编号[{self.order.OrderSysID}]")
            return
        if event.type == EventType.TRADE:
            self.log.info(f"on_trade回调触发 状态[成交成功] 委托编号[{event.payload.OrderID}] 股票代码[{event.payload.SecurityID}] 交易所[{event.payload.ExchangeID}] 成交方向[{event.payload.Direction}] 成交价格[{event.payload.Price}] 成交股数[{event.payload.Volume}] 成交日期[{event.payload.TradeDate}] 成交时间[{event.payload.TradeTime}]")
            self.status = TRADED
            self.log.info(f"on_trade回调触发 策略停止，注销监听函数")
            self.stop()
            return
    
    def stop(self):
        self.__engine.remove_strategy(self.id)
        self.log.info("注销策略监听函数")

    def on_tick():
        pass