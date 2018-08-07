from multiprocessing import Process
import os
import time

def info(title):
    print(title)
    print('module name:', __name__)
    print('parent process:', os.getppid())
    print('process id:', os.getpid())
    
def foo(name):
    info('function f')
    count = 0
    while(True):
        print('Thread {}, count: {}'.format(name, count))
        count+=1
        time.sleep(1)
        
    # print('hello', name)
def boo(name):
    info('function b')
    count = 0
    while(True):
        print('Thread {}, count: {}'.format(name, count))
        count+=1
        time.sleep(1)
    
if __name__ == '__main__':
    info('main line')
    p = Process(target=foo, args=('bob', ))
    j = Process(target=boo, args=('sarah', ))
    j.start()
    p.start()
    p.join()
    j.join()