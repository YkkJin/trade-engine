from .type import EventType


class EventEngine:

    def __init__(self, bus, strategy, quoter, trader):
        self.bus = bus
        self.strategy = strategy
        self.quoter = quoter
        self.trader = trader

    def run(self):
        self.bus.register(EventType.TICK, self.strategy.on_tick)
        self.quoter.subscribe(self.strategy.subscribe_list())
        self.bus.start()
