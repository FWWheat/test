import numpy as np
import random
import copy
import glob
import platform
import os
from src.circuit_utils import *

def read_npz_file(filename):
    data = np.load(filename, allow_pickle=True)
    return data

# Parameter
circuit_filename = 'benchmarks_circuits_graphs.npz'
label_filename = 'benchmarks_circuits_labels.npz'
gate_to_index = {'INPUT': 0, 'AND': 1, 'NOT': 2, 'BUFF': 3}
NO_LABEL = True

if __name__ == '__main__':
    new_graphs = {}
    new_labels = {}
    x_data_npz = './input_npz/' + circuit_filename
    label_npz = './input_npz/' + label_filename
    circuits = read_npz_file(x_data_npz)['circuits'].item()

    if not NO_LABEL:
        labels = read_npz_file(label_npz)['labels'].item()

    print(len(circuits))
    for circuit_idx, circuit_name in enumerate(circuits):
        x_data = []
        ori_mask = []
        if NO_LABEL:
            y = [0] * len(circuits[circuit_name]['x'])
        else:
            y = list(labels[circuit_name]['y'])
        for x in circuits[circuit_name]['x']:
            x_data.append([int(x[0]), int(x[1])])
            if len(x) == 10:
                ori_mask.append(int(x[-1]))
        edge_data = circuits[circuit_name]['edge_index']
        x_data, edge_data, y_data = branch_to_buffer(x_data, edge_data, gate_to_index, y)
        print('Added Buffer')

        for idx, x_data_info in enumerate(x_data):
            x_data[idx].append(0)
            x_data[idx].append(0.5)
            x_data[idx].append(0.5)
            x_data[idx].append(1)
            x_data[idx].append(-1)
            x_data[idx].append(-1)

        # x_data, edge_data, level_list, fanin_list, fanout_list = get_logic_level(x_data, edge_data)
        # # Generate x_data feature
        # PI_list = level_list[0]
        # x_data = generate_prob_cont(x_data, PI_list, level_list, fanin_list, gate_to_index)
        # x_data = generate_prob_obs(x_data, level_list, fanin_list, fanout_list, gate_to_index)
        # x_data, _ = identify_reconvergence(x_data, level_list, fanin_list, fanout_list)
        
        x_data = gen_mask(x_data, ori_mask)

        # Save 
        assert len(x_data) == len(y_data)
        print('[INFO] Convert ', circuit_name)
        new_graphs[circuit_name] = {'x': np.array(x_data).astype('float32'), 'edge_index': np.array(edge_data)}
        new_labels[circuit_name] = {'y': np.array(y_data)}

    circuits_file = './output_npz/benchmarks_circuits_graphs.npz'
    labels_file = './output_npz/benchmarks_circuits_labels.npz'

    np.savez_compressed(circuits_file, circuits=new_graphs)
    if not NO_LABEL:
        np.savez_compressed(labels_file, labels=new_labels)
    print(len(new_graphs))

