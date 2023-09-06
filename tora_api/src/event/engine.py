from .type import EventType
from ..log_handler.default_handler import DefaultLogHandler

class EventEngine:

    def __init__(self, bus,log):
        self.bus = bus
        self.log = log
        self.strategy_dict = {}
        #self.strategy = strategy
        # self.quoter = quoter
        # self.trader = trader

    def run(self):
        self.log.info(f"主引擎启动")
        # self.bus.register(EventType.TICK, self.strategy.on_tick)
        # self.bus.register(EventType.TRADE, self.strategy.on_trade)
        # self.bus.register(EventType.ORDER, self.strategy.on_order)
        # self.quoter.subscribe(self.strategy.subscribe_list())
        self.bus.start()

    def stop(self):
        self.log.info("主引擎关闭")
        #self.bus.unregister(EventType.TICK,self.strategy.on_tick)
        #self.bus.unregister(EventType.TRADE,self.strategy.on_trade)
        #self.bus.unregister(EventType.ORDER,self.strategy.on_order)
        self.bus.stop()
