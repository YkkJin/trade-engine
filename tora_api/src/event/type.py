from enum import Enum 


class EventType:
    TICK = 'EVENT_TICK'
    ORDER = 'EVENT_ORDER'
    TRADE = 'EVENT_TRADE'
    L2TICK = 'EVENT_L2TICK'
    L2OrdTrac = 'EVENT_L2OrdTrac'
    ...