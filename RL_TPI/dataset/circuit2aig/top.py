import argparse
import glob
import os
import sys
import platform
import matplotlib.pyplot as plt
import numpy as np
import circuit_utils as circuit_utils

output_filename_circuit = 'benchmarks_circuits_graphs'
output_filename_labels = 'benchmarks_circuits_labels'

graphs = {}
labels = {}

def read_file(file_name):
    f = open(file_name, "r")
    data = f.readlines()
    return data

def create_dataset(folder='./bench/', save_bench=True):
    gate_to_index = {"INPUT": 0, "AND": 1, "NAND": 2, "OR": 3, "NOR": 4, "NOT": 5, "XOR": 6}
    bench_folder = folder + "/*.bench"
    bench_idx = 0
    for file in glob.glob(bench_folder):
        if platform.system() == 'Windows':
            name = file.split("\\")
            name = name[1].split(".")
        else:
            name = file.split("/")
            name = name[-1].split(".")

        # if '001' not in name[0]:
        #     continue

        print("." * 10)
        print("No. %d Circuit Name: " % bench_idx, name[0])
        circuit_name = name[0]
        bench_idx += 1

        data = read_file(file)

        # updata the bench and also calculate the number of nodes
        data, num_nodes, index_map = circuit_utils.add_node_index(data)

        # base feature generation, node name, type, logic level
        data, edge_data, fanin_list, fanout_list = circuit_utils.feature_generation(data, gate_to_index)
        data = circuit_utils.rename_node_N(data)
        bod_data_len = len(data)
        print('[INFO] Before convertion # Node: {:}'.format(len(data)))

        # Convert to 2-fanin
        data, fanin_list, fanout_list = circuit_utils.convert_two_fanin(data, fanin_list, fanout_list, gate_to_index)
        print('[INFO] After convertion 2-fanin # Node: {:}'.format(len(data)))

        # Convert to aig
        data, fanin_list, fanout_list = circuit_utils.convert_aig(data, fanin_list, fanout_list, gate_to_index)
        print('[INFO] After convertion AIG # Node: {:}'.format(len(data)))

        # Generate Gate level
        # data, level_list = circuit_utils.get_level_list(data, fanin_list, fanout_list)
        for idx, x_data_info in enumerate(data):
            x_data_info.append(0)

        # calculate the logic depth of the circuit
        # print("Circuit Depth: ", len(level_list)-1)
        # num_nodes = len(data)
        # print("# Nodes : ", num_nodes)
        # PI_indexes = level_list[0]

        # After synthesize, some circuit only
        # if len(level_list) == 1 or num_nodes == 0:
        #     continue

        # adding COP measurements in feature set.
        print('Add the COP measurements.')
        x = data
        # x = circuit_utils.generate_prob_cont(x, PI_indexes, level_list, fanin_list)
        # x = circuit_utils.generate_prob_obs(x, level_list, fanin_list, fanout_list)
        for idx, x_data_info in enumerate(x):
            x[idx].append(0.5)
            x[idx].append(0.5)
            x[idx].append(1)

        '''
        x : list(list((str, int, int))), the node feature matrix with shape [num_nodes, num_node_features], the current dimension of num_node_features is 3, wherein 0th - node_name defined in bench (str); 1st - integer index for the gate type; 2nd - logic level; 3rd - C1, 4th - C0, 5th - Obs.
        '''

        print("Identifying reconvergence.")
        # x, _ = circuit_utils.identify_reconvergence(x, level_list, fanin_list, fanout_list)
        for idx, x_data_info in enumerate(x):
            x[idx].append(-1)
            x[idx].append(-1)
        
        '''
        x : list(list((str, int, int))), the node feature matrix with shape [num_nodes, num_node_features], the current dimension of num_node_features is 3, wherein 0th - node_name defined in bench (str); 1st - integer index for the gate type; 2nd - logic level; 3rd - C1; 4th - C0; 5th - Obs; 6th - fan-out, 7th - boolean recovengence, 8th - index of the source node (-1 for non recovengence).
        '''
        # circuit_utils.check_reconvergence(x_data_obj, sub_edge_data[index])
        # circuit_utils.circuit_statistics(name[0], x_data_obj, sub_edge_data[index])

        # Generate mask
        for idx in range(bod_data_len):
            x[idx].append(1)
        for idx in range(bod_data_len, len(x)):
            x[idx].append(0)
        
        # Save AIG bench
        print('Saving Bench')
        if save_bench:
            file_name = './bench_aig/'+circuit_name+'.bench'
            circuit_utils.save_bench(file_name, x, fanin_list, fanout_list, gate_to_index)

        # Map AND, NOT to 1, 2
        for idx, x_data_info in enumerate(x):
            if x_data_info[1] == gate_to_index['INPUT']:
                x[idx][1] = 0
            elif x_data_info[1] == gate_to_index['AND']:
                x[idx][1] = 1
            elif x_data_info[1] == gate_to_index['NOT']:
                x[idx][1] = 2

        # Rewrite edge_data
        edge_data = []
        for idx, x_data_info in enumerate(x):
            for fanout_idx in fanout_list[idx]:
                edge_data.append([idx, fanout_idx])

        # Convert node name (str) to node index (int)
        x = circuit_utils.rename_node(x)
        graphs[name[0]] = {'x': np.array(x).astype('float32'), "edge_index": np.array(edge_data)}
        
        
    # save to numpy npz compressed format
    print('Saving...')
    np.savez_compressed(output_filename_circuit, circuits=graphs)


if __name__ == '__main__':
    create_dataset('./bench')
    print('Finish circuit extraction.')
