import web.model.model_tfidf.getSim as tfidf
from web.model.model_ubh.model_same_time import UserBoughtHistory
from web.model.myutil import func_timer, factor_data_dict, update_data_dict, \
    update_data_dict_with_factor, dict2list_sorted_by_value, dict_filter


class MergedModel:

    LimitNum = 10
    SimilarThreshold = 0.6

    def __init__(self):
        self.model_ubh = UserBoughtHistory()
        self.model_tfidf = tfidf.model_tfidf

    def get_cat(self, item_id):
        return self.model_tfidf.get_cat(item_id)

    def remove_items_same_cat(self, item_dict: dict, item_id):
        cat_id = self.get_cat(item_id)
        for k, v in item_dict:
            if cat_id == self.get_cat(k):
                item_dict.pop(k)

    def __get_sim_items(self, item_id):
        sim_high, sim_low = self.model_tfidf.get_sim_items(item_id)
        return sim_high

    def __expand_search_input(self, item_id):  # -> dict
        result = self.__get_sim_items(item_id)
        result[item_id] = 1
        return result


    @func_timer
    def __get_normal_result(self, item_id):
        result = self.model_tfidf.get_match_items(item_id)
        dict_filter(lambda x: x > MergedModel.SimilarThreshold, result)

        result_ubh = self.model_ubh.get_match_dict(item_id)
        update_data_dict(result, result_ubh)
        return result

    def get_result(self, item_id):
        query_input = {item_id: 1.0}
        limit_num = MergedModel.LimitNum

        input_sim_dict = self.__get_sim_items(item_id)
        input_sim_list = dict2list_sorted_by_value(input_sim_dict)[:limit_num]
        update_data_dict(query_input, input_sim_list)

        result = {}
        watch_dog = limit_num
        for sim_item, similarity in query_input.items():
            if watch_dog <= 0:
                break
            watch_dog -= 1
            update_data_dict_with_factor(result, self.__get_normal_result(sim_item), similarity)

        result.pop(item_id)
        cat_id = self.get_cat(item_id)
        for k in list(result.keys()):
            if self.get_cat(k) == cat_id:
                result.pop(k)

        result = dict2list_sorted_by_value(result)[:limit_num]

        return result


if __name__ == '__main__':
    item_id = "22943"
    merged_model = MergedModel()
    print("result: {}".format(merged_model.get_result(item_id)))
