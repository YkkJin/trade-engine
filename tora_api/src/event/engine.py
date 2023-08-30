from .type import EventType


class EventEngine:

    def __init__(self, bus):
        self.bus = bus
        #self.strategy = strategy
        # self.quoter = quoter
        # self.trader = trader

    def run(self):
        #self.bus.register(EventType.TICK, self.strategy.on_tick)
        #self.bus.register(EventType.TRADE, self.strategy.on_trade)
        #self.bus.register(EventType.ORDER, self.strategy.on_order)
        # self.quoter.subscribe(self.strategy.subscribe_list())
        self.bus.start()
