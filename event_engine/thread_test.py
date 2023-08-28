import threading
from abc import ABCMeta, abstractmethod

class Notice:
    def __init__(self):
        self.observers = []
    
    def attach(self,observer):
        self.observers.append(observer)
    
    def detach(self,observer):
        self.observers.remove(observer)
    
    def notify(self):
        for obsers in self.observers:
            obsers.update(self)

class Observer(metaclass = ABCMeta):
    @abstractmethod
    def update(self,notice):
        pass

class StaffNotice(Notice):
    def __init__(self,company_info):
        super().__init__()
        self.__company_info = company_info
    @property
    def company_info(self):
        return self.__company_info
    @company_info.setter
    def company_info(self,info):
        self.__company_info = info
        self.notify()
        #print('setting')
    
class Staff(Observer):
    def __init__(self):
        self.company_info = None
    
    def update(self,notice):
        #print(notice.company_info)
        self.company_info = notice.company_info
    

notice = StaffNotice('init info')
s1 = Staff()
s2 = Staff()
print(s1.company_info)
print(s2.company_info)

notice.attach(s1)
notice.attach(s2)

notice.company_info = 'new message'

print(s1.company_info)
#print(notice.observers)


