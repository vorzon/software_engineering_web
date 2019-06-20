import web.model.model_tfidf.getSim as tfidf
from web.model.model_ubh.model_same_time import UserBoughtHistory

if __name__ == '__main__':
    item_id = "22943"

    model_ubh = UserBoughtHistory()
    model_ubh_res = model_ubh.get_match_dict(item_id)

    print(model_ubh_res)

    model_tfidf = tfidf.model_tfidf
    model_tfidf_res = model_tfidf.get_match_items(item_id)

    print("tf-idf result {}:{}".format(item_id, model_tfidf_res))
