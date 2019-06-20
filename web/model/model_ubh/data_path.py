
data_dir = "./dataset/raw/"

user_bought_history = data_dir + "user_bought_history.txt"
dim_fashion_matchsets = data_dir + "dim_fashion_matchsets.txt"
dim_items = data_dir + "dim_items.txt"

def get_file_lines(path:str):
    f = open(path, 'r')
    return f.readlines()

