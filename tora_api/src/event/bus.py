from queue import Queue, Empty , LifoQueue
from threading import Thread 
from datetime import datetime
from .event import Event 
from .type import EventType 
from collections import defaultdict
import time
from streamlit.runtime.scriptrunner.script_run_context import add_script_run_ctx
import streamlit as st
 
class EventBus:
    def __init__(self):
        self.__active = False 
        self.__thread = Thread(target = self.__run)
        self.__queue = Queue()
        self.__lifoqueue = LifoQueue() 
        self.__handlers = defaultdict(list)

    
    def __run(self):
        
        while self.__active:
            print('bus running 1')
            time.sleep(1)
            while not self.__lifoqueue.empty() or not self.__queue.empty():
                print('bus running 2')
                st.write(f"bus running {datetime.now().second}")
                event = self.__lifoqueue.get()
                self.__process(event)
                event = self.__queue.get()
                self.__process(event)


    def __process(self,event):
        if event.type in self.__handlers:
            [handler(event) for handler in self.__handlers[event.type]]
        handlers = self.__handlers[event]
    

    def start(self):
        self.__active = True 
        self.__thread = add_script_run_ctx(self.__thread)
        self.__thread.start()
    
    def stop(self):
        self.__active = False 
        self.__thread.join() 

    def put_fifo(self,event: Event):
        self.__queue.put(event)
    
    def put_lifo(self,event: Event):
        self.__lifoqueue.put(event)
    
    def register(self,type,handler):
        handlers = self.__handlers[type]
        if handler not in handlers:
            handlers.append(handler)
    
    def unregister(self,type,handler):
        handlers: list = self._handlers[type]
        if handler in handlers:
            handlers.remove(handler)

        if not handlers:
            self._handlers.pop(type)

