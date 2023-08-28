from threading import Thread
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict
from collections.abc import Callable

from datetime import datetime
from time import sleep
from queue import LifoQueue

import numpy as np

class EventType(Enum):
    BAR = "BAR"

@dataclass()
class Event:
    def __init__(self,type: EventType, payload: dict):
        self.type = type 
        self.payload = payload

@dataclass(frozen=True)
class Bar:
    open : float
    high : float
    low : float
    close : float
    volume : float
    timestamp :datetime
    time : str

class EventBus:
    def __init__(self,sample_freq:float = 0.2):
        self.topics = defaultdict(list)
        self.events = LifoQueue()
        self.sample_freq = sample_freq
        self.thread = Thread(target = self.blocking_run)
    def subscribe(self, event_type: EventType, callback: Callable):
        self.topics[event_type].append(callback)

    def push(self,event:Event):
        self.events.put(event)

    def blocking_run(self):

        while True:
            while not self.events.empty():
                event = self.events.get()
                _callables = self.topics[event.type]
                for _callable in _callables:
                    _callable(event.payload)
            sleep(self.sample_freq)
    
    def start(self):
        self.thread.start()

class Strategy:

    def on_bar(self,bar:Bar):
        latency = datetime.now() - bar.timestamp
        print(f'------now is {datetime.now().minute} : {datetime.now().second}-------')
        print(f'received {bar.open} ,{bar.time} with latency {latency.microseconds/1000} ms')
        sleep(1)


class DataFeed(ABC):
    @abstractmethod
    def start(self):
        pass

class Engine:

    def __init__(self,bus:EventBus, strategy:Strategy, feed: DataFeed):
        self.bus = bus
        self.strategy = strategy
        self.feed = feed

    def run(self):
        bus.subscribe(EventType.BAR, self.strategy.on_bar)
        self.bus.start()
        self.feed.start()

        while True:
            sleep(0.05)



class DummyBarFeed(DataFeed):

    def __init__(self,bus:EventBus):
        self.bus = bus
        self.thread= Thread(target = self._run)

    def start(self):
        self.thread.start()

    def _run(self):
        for i in range(10000000):
            sleep(0.01)
            bar = Bar(
                    open = i,
                    high=i,
                    low=i,
                    close=i, 
                    volume = i,
                    timestamp = datetime.now(),
                    time = str(datetime.now().minute)+':' +str(datetime.now().second)
                    # open = 100 *i,
                    # high=200 *i,
                    # low=100 *i,
                    # close=100*i, 
                    # volume = 200000 *i,
                    # timestamp = datetime.now()
            )
            event = Event(type = EventType.BAR,
                        payload = bar
                        )
            self.bus.push(event)




if __name__ == "__main__":

    bus = EventBus(sample_freq= 0.05)
    start = Strategy()
    feed = DummyBarFeed(bus)
    engine = Engine(bus,strategy = start, feed= feed)

    engine.run()
