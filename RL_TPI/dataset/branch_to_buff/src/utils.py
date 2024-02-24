import numpy as np

def read_npz_file(filename):
    data = np.load(filename, allow_pickle=True)
    return data
    