from .type import EventType

class Event:
    '''
    事件对象
    '''
    def __init__(self,tyoe: EventType, payload: dict)