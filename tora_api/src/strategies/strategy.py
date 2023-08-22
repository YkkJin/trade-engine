from ..event.event import Event

class Strategy:
    def __init__(self):
        self.name = 'test'

    def on_tick(self,event: Event):
        print(f"Strategy {self.name} received {event.type} with payload {event.payload}")