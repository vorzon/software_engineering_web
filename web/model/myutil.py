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


def save_to_file(ob, path: str):
    with open(path, 'wb') as f:
        pickle.dump(ob, f)


def load_from_file(path: str):
    with open(path, 'rb') as f:
        return pickle.load(f)


def file_exist(path: str):
    return os.path.exists(path)


def factor_data_dict(data_dict: dict, factor: float):
    data_dict = data_dict.copy()
    for k, v in data_dict.items():
        data_dict[k] = v*factor
    return data_dict


def update_data_dict(source: dict, another):
    ano_type = type(another)

    if ano_type == dict:
        another = another.items()

    for k, v in another:
        if k in source:
            source[k] += v
        else:
            source[k] = v


def update_data_dict_with_factor(data_dict: dict, another: dict, factor: float):
    another = factor_data_dict(another, factor)
    update_data_dict(data_dict, another)


def dict2list_sorted_by_value(input:dict):
    list_from_input = list((k,v) for k,v in input.items())
    list_from_input.sort(key=lambda x:x[1], reverse=True)
    return list_from_input
