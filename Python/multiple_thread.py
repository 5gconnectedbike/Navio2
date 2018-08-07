from multiprocessing import Process
import os

def info(title):
    print(title)
    print('module name:', __name__)
    print('parent process:', os.getppid())
    print('process id:', os.getpid())
    
def foo(name):
    info('function f')
    print('hello', name)
    
if __name__ == '__main__':
    info('main line')
    p = Process(target=foo, args=('bob', ))
    j = Process(target=foo, args=('sarah', ))
    j.start()
    p.start()
    p.join()
    j.join()