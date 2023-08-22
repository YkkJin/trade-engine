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
