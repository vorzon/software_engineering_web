
import numpy as np
import math
import re
import pickle
import web.model.path_util as path_util

class ItemSim():
    def __init__(self, path_dict_collid_items, path_dict_item_collids, path_dict_item_cat, path_dict_item_terms, path_dict_cat_items, path_dict_term_cat_items):
        self.__sim_threshold = 0.3
        self.__dict_term_cat_idf = {}
        self.__sim_all = {}  # item-{item_sim: score}高于阈值的相似商品
        self.__sim_low = {}  # item-{item_sim: score}低于阈值的相似商品
        self.__read_dict(path_dict_collid_items, path_dict_item_cat, path_dict_item_terms, path_dict_item_collids, path_dict_cat_items, path_dict_term_cat_items)

    def __read_dict(self, path_dict_collid_items, path_dict_item_cat, path_dict_item_terms, path_dict_item_collids, path_dict_cat_items, path_dict_term_cat_items):
        with open(path_dict_collid_items, 'rb') as f:
            self.__dict_collid_items = pickle.load(f)
        with open(path_dict_item_cat, 'rb') as f:
            self.__dict_item_cat = pickle.load(f)
        with open(path_dict_item_terms, 'rb') as f:
            self.__dict_item_terms = pickle.load(f)
        with open(path_dict_item_collids, 'rb') as f:
            self.__dict_item_collids = pickle.load(f)
        with open(path_dict_cat_items, 'rb') as f:
            self.__dict_cat_items = pickle.load(f)
        with open(path_dict_term_cat_items, 'rb') as f:
            self.__dict_term_cat_items = pickle.load(f)

    def get_sim_items(self, item_id):
        query = []
        docs = {}
        sim = {}
        sim2 = {}  # 记录低于阈值的相似商品
        cat = self.__dict_item_cat[item_id]
        terms = self.__dict_item_terms[item_id]
        for term in terms:
            # wi of query
            tf_q = float(terms.count(term) / len(terms))
            term_cat = term + "_" + cat
            # idf = getIDF(term, cat, dict_term_cat_items, dict_item_cat, dict_item_terms)
            if term_cat not in self.__dict_term_cat_idf:
                idf = self.__getIDF(term, cat, self.__dict_term_cat_items, self.__dict_cat_items)
                self.__dict_term_cat_idf[term_cat] = idf
            else:
                idf = self.__dict_term_cat_idf[term_cat]
            query.append(tf_q * idf)

            # wi of di
            for item in self.__dict_term_cat_items[term_cat]:
                if item in self.__sim_all and item_id in self.__sim_all[item]:
                    sim[item] = self.__sim_all[item][item_id]
                    continue
                else:
                    if item in self.__sim_low and item_id in self.__sim_low[item]:
                        sim2[item] = self.__sim_low[item][item_id]
                        continue
                    tf_di = float(self.__dict_item_terms[item].count(term) / len(self.__dict_item_terms[item]))
                    if item not in docs:
                        if len(query) == 1:
                            docs[item] = [tf_di * idf]
                        else:
                            docs[item] = [0] * (len(query) - 1)
                            docs[item].append(tf_di * idf)
                    else:
                        if len(docs[item]) == len(query):
                            continue
                        if len(docs[item]) < len(query) - 1:
                            temp = [0] * (len(query) - len(docs[item]) - 1)
                            docs[item].extend(temp)
                        docs[item].append(tf_di * idf)

        for di in docs:
            if len(docs[di]) < len(query):
                temp = [0] * (len(query) - len(docs[di]))
                docs[di].extend(temp)

            temp = self.__cos_sim(query, docs[di])
            if temp >= self.__sim_threshold:
                sim[di] = temp
            else:
                sim2[di] = temp
        # return sorted(sim.items(), key=lambda d:d[1], reverse = True)
        return sim, sim2

    def get_match_items(self, item_id):
        dict_total_item_match = {}
        if item_id not in self.__dict_item_collids:
            return []

        for collid in self.__dict_item_collids[item_id]:
            for item_match in self.__dict_collid_items[collid]:
                if (item_match in self.__dict_item_cat and
                            self.__dict_item_cat[item_match] == self.__dict_item_cat[item_id]):
                    continue
                self.__sim_all[item_match], self.__sim_low[item_match] = self.get_sim_items(item_match)
                sim = self.__sim_all[item_match]
                for di in sim:
                    if di in dict_total_item_match:
                        dict_total_item_match[di] = max(sim[id], dict_total_item_match[id])
                    else:
                        dict_total_item_match[di] = sim[di]
        dict_total_item_match = sorted(dict_total_item_match.items(), key=lambda d: d[1], reverse=True)
        return dict_total_item_match

    def __cos_sim(self, vec_a, vec_b):
        vec_a = np.array(vec_a, dtype=float)
        vec_b = np.array(vec_b, dtype=float)
        num = np.dot(vec_a, vec_b)
        demon = np.linalg.norm(vec_a) * np.linalg.norm(vec_b)
        if demon == 0:
            return 0
        cos = num / demon
        return cos

    # def __create_dict_itemfile(self, path):
    #     """
    #     读取商品信息，建立item-cat,item-terms,term_cat-items, cat-terms个索引
    #     :param path: 文件路径
    #     :return: 三个索引
    #     """
    #     with open(path, 'r') as f:
    #         dict_item_cat = {}
    #         dict_item_terms = {}
    #         dict_cat_items = {}
    #         dict_term_cat_items = {}
    #         # print(f.readline(10))
    #         for line in f:
    #             # 每一行分为item, cat, terms三部分
    #             arr = line.split()
    #             if len(arr) < 3:
    #                 continue
    #             # print(arr)
    #             dict_item_cat[arr[0]] = arr[1]
    #             if arr[1] not in dict_cat_items:
    #                 dict_cat_items[arr[1]] = [arr[0]]
    #             else:
    #                 dict_cat_items[arr[1]].append(arr[0])
    #             dict_item_terms[arr[0]] = arr[2].split(",")
    #             for term in arr[2].split(","):
    #                 term_cat = term + "_" + arr[1]
    #                 if term_cat not in dict_term_cat_items:
    #                     dict_term_cat_items[term_cat] = [arr[0]]
    #                 else:
    #                     dict_term_cat_items[term_cat].append(arr[0])
    #     return dict_item_terms, dict_item_cat, dict_cat_items, dict_term_cat_items

    # def __create_dict_clothmatch(self, path):
    #     dict_item_collids = {}
    #     dict_collid_items = {}
    #     with open(path, 'r') as f:
    #         for line in f:
    #             arr = line.split()
    #             item_list = re.split(';|,', arr[1])
    #             dict_collid_items[arr[0]] = item_list
    #             for item in item_list:
    #                 if item not in dict_item_collids:
    #                     dict_item_collids[item] = [arr[0]]
    #                 else:
    #                     dict_item_collids[item].append(arr[0])
    #     return dict_item_collids, dict_collid_items

    def __getIDF(self, term, cat, dict_term_cat_items, dict_cat_items):
        term_cat = term + "_" + cat
        ni = len(dict_term_cat_items[term_cat])
        N = len(dict_cat_items[cat])
        # temp = set(dict_term_items[term])
        # for item in temp:
        #     if dict_item_cat[item] == cat:
        #         ni += 1
        # for item in dict_item_terms:
        #     if dict_item_cat[item] == cat:
        #         N += 1

        if N != 0:
            # print(float(ni / N))
            return math.log(float(N / ni), math.e)
        else:
            return 0



def create_dict_itemfile(path, path_dict_item_cat, path_dict_item_terms, path_dict_cat_items, path_dict_term_cat_items,):
    """
    读取商品信息，建立term_cat-items, cat-terms索引
    :param path: 文件路径
    :return: 三个索引
    """
    with open(path, 'r') as f:
        dict_item_cat = {}
        dict_item_terms = {}
        dict_cat_items = {}
        dict_term_cat_items = {}
        #print(f.readline(10))
        for line in f:
            #每一行分为item, cat, terms三部分
            arr = line.split()
            if len(arr) < 3:
                continue
            #print(arr)
            dict_item_cat[arr[0]] = arr[1]
            if arr[1] not in dict_cat_items:
                dict_cat_items[arr[1]] = [arr[0]]
            else:
                dict_cat_items[arr[1]].append(arr[0])
            dict_item_terms[arr[0]] = arr[2].split(",")
            for term in arr[2].split(","):
                term_cat = term + "_" + arr[1]
                if term_cat not in dict_term_cat_items:
                    dict_term_cat_items[term_cat] = [arr[0]]
                else:
                    dict_term_cat_items[term_cat].append(arr[0])
        with open(path_dict_cat_items, 'wb') as f:
            pickle.dump(dict_cat_items, f)
        with open(path_dict_term_cat_items, 'wb') as f:
            pickle.dump(dict_term_cat_items, f)
        with open(path_dict_item_cat, 'wb') as f:
            pickle.dump(dict_item_cat, f)
        with open(path_dict_item_terms, 'wb') as f:
            pickle.dump(dict_item_terms, f)
    #return dict_cat_items, dict_term_cat_items

def create_dict_clothmatch(path, path_dict_item_collids, path_dict_collid_items):
    dict_item_collids = {}
    dict_collid_items = {}
    with open(path, 'r') as f:
        for line in f:
            arr = line.split()
            item_list = re.split(';|,', arr[1])
            dict_collid_items[arr[0]] = item_list
            for item in item_list:
                if item not in dict_item_collids:
                    dict_item_collids[item] = [arr[0]]
                else:
                    dict_item_collids[item].append(arr[0])
        with open(path_dict_item_collids, 'wb') as f:
            pickle.dump(dict_item_collids, f)
        with open(path_dict_collid_items, 'wb') as f:
            pickle.dump(dict_collid_items, f)
    #return dict_item_collids, dict_collid_items


path_dict_item_collids = path_util.make_real_path("index_item_collids.pk")
path_dict_cat_items = path_util.make_real_path("index_cat_items.pk")
path_dict_term_cat_items = path_util.make_real_path("index_term_cat_items.pk")
path_dict_item_terms = path_util.make_real_path("index_item_terms.pk")
path_dict_collid_items = path_util.make_real_path("index_collid_items.pk")
path_dict_item_cat = path_util.make_real_path("index_item_cat.pk")

model_tfidf = ItemSim(path_dict_collid_items, path_dict_item_collids, path_dict_item_cat,
                      path_dict_item_terms, path_dict_cat_items, path_dict_term_cat_items)

if __name__ == "__main__":
    items_path = "./dim_items.txt"
    clothmatch_path = "./dim_fashion_matchsets.txt"

    #create_dict_clothmatch(clothmatch_path, path_dict_item_collids, path_dict_collid_items)
    #create_dict_itemfile(items_path, path_dict_item_cat, path_dict_item_terms, path_dict_cat_items, path_dict_term_cat_items,)
    res = model_tfidf.get_match_items("2741506")
    print(res)

    # path_save = "./index.pkl"

    # items_path = "./test_item.txt"
    # clothmatch_path = "./test_match.txt"

    # item_sim = ItemSim(clothmatch_path, items_path)
    # res = item_sim.get_match_items("2741506")
    # print(res)

    # path_save = "./index.pkl"
    # path_sim_index = "./sim_index.pkl"
    # path_sim_low_index = "./sim_low_index.pkl"

