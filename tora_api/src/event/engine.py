from .type import EventType

class EventEngine:

    def __init__(self,bus,strategy):
        self.bus = bus
        self.strategy = strategy 
    
    def run(self):
        self.bus.register(EventType.TICK,self.strategy.on_tick)
        self.bus.start()
