from queue import Queue, Empty , LifoQueue
import multiprocessing as mp
from datetime import datetime
from .event import Event 
from .type import EventType 
from collections import defaultdict
import time

import streamlit as st


class EventBus:
    def __init__(self):
        self.__active = True 
        self.__queue = mp.Queue()
        self.q_handlers = mp.Queue()
        #self.__lifoqueue = LifoQueue() 
        self.handlers = defaultdict(list)



    
    def run(self):
        
        while self.__active:
            print('bus running 1')
            time.sleep(1)
            while not  self.__queue.empty():
                print('bus running 2')
                #st.write(f"bus running {datetime.now().second}")
                event = self.__queue.get()
                print(event)
                self.process(event)


    def process(self,event):
        print('bus processing event')
        print(f"within in process type and handlers are {event.type} , {self.handlers}, id is {id(self.handlers)}")
        if event.type in self.handlers:
            for handler in self.handlers[event.type]:
                print(f'handler is {handler}, event.type is {event.type}')
                handler(event)
            #[handler(event) for handler in self.handlers[event.type]]
        #handlers = self.handlers[event]
    



    def put_fifo(self,event: Event):
        self.__queue.put(event)
    
    #def put_lifo(self,event: Event):
    #    self.__lifoqueue.put(event)
    def q_register(self):
        self.handlers = self.q_handlers.get()

    def register(self,type,handler):
        handlers = self.handlers[type]
        if handler not in handlers:
            self.handlers[type].append(handler)
    
    def unregister(self,type,handler):
        handlers: list = self._handlers[type]
        if handler in handlers:
            handlers.remove(handler)

        if not handlers:
            self._handlers.pop(type)

