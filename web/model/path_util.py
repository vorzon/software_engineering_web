import os.path

data_dir = "model_data/"

def make_real_path(filename):
    return os.path.join(data_dir, filename)
