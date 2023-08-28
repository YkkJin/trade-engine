from threading import Thread
from queue import Queue
from time import sleep


queue = Queue(maxsize=5)

def put(q):
    for i in range(10):
        q.put(i,block=False)
        sleep(0.5)
    print('wait for other threa to get')
    sleep(1)

def get(q):
    while True:
        print(f'getting item {q.get()}')
        sleep(2)

t1 = Thread(target = put,args=(queue,))
t2 = Thread(target = get,args=(queue,))

t1.start()
t2.start()