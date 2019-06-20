#  -*- coding: utf-8 -*-
import time
import os

import web.model.model_ubh.data_path as data_path
import web.model.model_ubh.myutil as myutil

class Record:
    def __init__(self, user_id, item_id, buy_time):
        self.user_id = user_id
        self.item_id = item_id
        self.buy_time = buy_time

def __add_similar_pair(final_result:dict, item1, item2):
    if item1 in final_result:
        sub_dict = final_result[item1]
        if item2 in sub_dict:
            sub_dict[item2] += 1
        else:
            sub_dict[item2] = 1
    else:
        final_result[item1] = {item2:1}

def add_pair(final_result:dict, item1, item2):
    if item1 == item2:
        return
    __add_similar_pair(final_result, item1, item2)
    __add_similar_pair(final_result, item2, item1)

item_same_day_dict_path = './item_same_day.pkl'


@myutil.func_timer
def get_user_bought_history(rebuild=True):
    if not rebuild and myutil.file_exist(item_same_day_dict_path):
        return myutil.load_from_file(item_same_day_dict_path)

    limit = 10000000
    num_deal = 0
    user_dict = {}
    final_result = {}

    for line in data_path.get_file_lines(data_path.user_bought_history):
        arr = line.split()

        user_id = arr[0]
        item_id = arr[1]
        buy_time = arr[2][:6] #get to month

        if user_id in user_dict:
            buy_time_dict = user_dict[user_id]
            if buy_time not in buy_time_dict:
                buy_time_dict[buy_time] = [item_id]
            else:
                buy_time_dict[buy_time].append(item_id)
        else:
            user_dict[user_id] = {buy_time:[item_id]}

        num_deal += 1
        if num_deal > limit:
            break

    for user_id, buy_time_dict in user_dict.items():
        pre_time = time.time()
        for _, item_same_time in buy_time_dict.items():
            num_item = len(item_same_time)
            for i in range(num_item):
                for k in range(i+1, num_item):
                    add_pair(final_result, item_same_time[i], item_same_time[k])
        cost = pre_time - time.time()
        print('deal-{} user-{} cost-time-{}'.format(num_deal, user_id, cost))

    myutil.save_to_file(final_result, item_same_day_dict_path)
    return final_result


class UserBoughtHistory:
    def __init__(self):
        self.data = get_user_bought_history(rebuild=False)

    def get_match_dict(self, item_id):
        if item_id in self.data:
            return self.data[item_id]
        else:
            return {}


if __name__ == "__main__":
    item_same_day = get_user_bought_history(rebuild=False)
    for k,v in item_same_day.items():
        print("{}: {}".format(k, v))
    print("len: {}".format(len(item_same_day)))
