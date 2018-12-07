# @Time   : 2018-9-10
# @Author : zxh
import threading
import traceback
import os
import datetime
import sys
_file_path = os.path.realpath(__file__)

_src_index = _file_path.rfind('src')
if _src_index == -1:
    _file_path = sys.argv[0]
    _src_index = _file_path.rfind('src')
if _src_index == -1:
    PROJECT_PATH = None
else:
    PROJECT_PATH =_file_path[0:_src_index]

print('PROJECT PATH:',PROJECT_PATH)
print()


def relative_project_path(*args):
    if PROJECT_PATH is None:
        raise Exception('PROJECT_PATH is None')
    return os.path.join(PROJECT_PATH, *args)
# ...
def wrapper_mutex(instance, func, mutex_name='', timeout=1):
    mutex_name = '_mutex_' + mutex_name
    mutex = None
    if mutex_name in dir(instance):
        mutex = instance.__getattribute__(mutex_name)
    else:
        mutex = threading.Lock()
        instance.__setattr__(mutex_name, mutex)
    def new_func(*args):
        if mutex.acquire(timeout=timeout):
            r = None
            try:
                r = func(*args)
            except:
                traceback.print_exc()
            mutex.release()
            return r
        else:
            print(func.__name__, 'acquire timeout')
    instance.__setattr__(func.__name__, new_func)

def get_sort_index(a, reverse=True):#默认降序
    b = [i for i in range(len(a))]
    c = list(zip(a, b))
    c.sort(key = lambda x: x[0], reverse=reverse)
    _, b = zip(*c)
    return b

def this_time():
    now = datetime.datetime.now()
    date = now.strftime('%Y-%m-%d')
    t = now.strftime('%H-%M-%S')
    return date, t

def today():
    return datetime.datetime.now().strftime('%Y-%m-%d')

def yesterday():
    return (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')

__all__ = ['wrapper_mutex', 'relative_project_path', 'get_sort_index', 'today', 'this_time']


