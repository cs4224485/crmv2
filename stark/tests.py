from django.test import TestCase

# Create your tests here.

from threading import current_thread, Thread, Lock
import os, time


def task():
    time.sleep(3)
    print('%s start to run' % current_thread().getName())

    global n
    temp = n
    time.sleep(0.5)
    n = temp - 1


if __name__ == '__main__':
    n = 100
    lock = Lock()
    start_time = time.time()
    for i in range(100):
        t = Thread(target=task)
        t.start()
        t.join()
    stop_time = time.time()
    print('主:%s n:%s' % (stop_time - start_time, n))

'''
100 Thread-1 start to run
101 Thread-2 start to run
102 ......
103 Thread-100 start to run
104 主:350.6937336921692 n:0 #耗时是多么的恐怖
105 '''
