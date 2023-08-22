from .type import EventType

class Event:
    '''
    事件对象
    '''
    def __init__(self,type: EventType, payload: dict):
        self.type = type 
        self.payload = payload