from .type import EventType
from pydantic import BaseModel

class Event:
    '''
    事件对象
    '''
    def __init__(self, event_type: EventType, payload: BaseModel):
        self.type = event_type
        self.payload = payload
