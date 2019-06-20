from functools import wraps
import pickle
import time
import os

def func_timer(function):
    '''
    用装饰器实现函数计时
    :param function: 需要计时的函数
    :return: None
    '''
    @wraps(function)
    def function_timer(*args, **kwargs):
        print('[Function: {name} start...]'.format(name=function.__name__))
        t0 = time.time()
        result = function(*args, **kwargs)
        t1 = time.time()
        print('[Function: {name} finished, spent time: {time:.2f}s]'.format(name=function.__name__, time=t1 - t0))
        return result
    return function_timer

def save_to_file(ob, path:str):
    with open(path, 'wb') as f:
        pickle.dump(ob, f)

def load_from_file(path:str):
    with open(path, 'rb') as f:
        return pickle.load(f)

def file_exist(path: str):
    return os.path.exists(path)
