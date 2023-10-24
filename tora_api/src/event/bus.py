from queue import Queue, Empty 
from threading import Thread 
from datetime import datetime
from .event import Event 
from .type import EventType 
from collections import defaultdict


class EventBus:
    def __init__(self):
        self.__active = False 
        self.__thread = Thread(target = self.__run)
        self.__queue = Queue()
        self.__handlers = defaultdict(list)

    
    def __run(self):
        while self.__active:
            try:
                event = self.__queue.get(block = True, timeout = 1)
                self.__process(event)
            except Empty:
                pass

    def __process(self,event):
        if event.type in self.__handlers:
            [handler(event) for handler in self.__handlers[event.type]]

    

    def start(self):
        self.__active = True 
        self.__thread.start()
    
    def stop(self):
        self.__active = False 
        self.__thread.join() 

    def put(self,event: Event):
        self.__queue.put(event)
    
    def register(self,type,handler):
        handlers = self.__handlers[type]
        if handler not in handlers:
            handlers.append(handler)
    
    def unregister(self,type,handler):
        handlers: list = self.__handlers[type]
        if handler in handlers:
            handlers.remove(handler)

        if not handlers:
            self.__handlers.pop(type)

