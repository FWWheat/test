from numpy.random import randint
from collections import Counter

def get_gate_type(gate_type, gate_to_idx):
    for symbol in gate_to_idx.keys():
        if gate_to_idx[symbol] == gate_type:
            return symbol
    raise('Unsupport Gate Type: ', gate_type)

def get_gate_type_num(line, gate_to_index):
    vector_row = -1
    for (gate_name, index) in gate_to_index.items():
        if gate_name in line:
            vector_row = index

    if vector_row == -1:
        raise KeyError('[ERROR] Find unsupported gate', vector_row)

    return vector_row

def new_node(name2idx, x_data, node_name, gate_type):
    x_data.append([node_name, gate_type])
    name2idx[node_name] = len(name2idx)

def branch_to_buffer(x_data, edge_index, gate_to_index, y_data):
    fanout_list = []
    for x_data_info in x_data:
        fanout_list.append([])
    for edge in edge_index:
        fanout_list[edge[0]].append(edge[1])

    for idx, fanout in enumerate(fanout_list):
        if len(fanout) > 1:
            for k, fanout_idx in enumerate(fanout):
                buff_name = len(x_data)
                new_node({}, x_data, buff_name, get_gate_type_num('BUFF', gate_to_index))
                fanout_list.append([fanout_idx])
                fanout_list[idx][k] = len(x_data) - 1
                y_data.append(y_data[idx])

    edge_index = []
    for idx, fanout in enumerate(fanout_list):
        for fanout_idx in fanout:
            edge_index.append([idx, fanout_idx])
    return x_data, edge_index, y_data

def get_logic_level(x_data, edge_index_data):
    fanout_list = []
    fanin_list = []
    bfs_q = []
    x_data_level = [-1] * len(x_data)
    max_level = 0
    for idx, x_data_info in enumerate(x_data):
        fanout_list.append([])
        fanin_list.append([])
        if x_data_info[1] == 0:
            bfs_q.append(idx)
            x_data_level[idx] = 0
    for edge in edge_index_data:
        fanout_list[edge[0]].append(edge[1])
        fanin_list[edge[1]].append(edge[0])
    while len(bfs_q) > 0:
        idx = bfs_q[-1]
        bfs_q.pop()
        tmp_level = x_data_level[idx] + 1
        for next_node in fanout_list[idx]:
            if x_data_level[next_node] < tmp_level:
                x_data_level[next_node] = tmp_level
                bfs_q.insert(0, next_node)
                if x_data_level[next_node] > max_level:
                    max_level = x_data_level[next_node]
    level_list = []
    for level in range(max_level+1):
        level_list.append([])
    if -1 in x_data_level:
        print('Wrong')
        raise
    else:
        if max_level == 0:
            level_list = [[]]
        else:
            for idx in range(len(x_data)):
                x_data[idx].append(x_data_level[idx])
                level_list[x_data_level[idx]].append(idx)
    return x_data, edge_index_data, level_list, fanin_list, fanout_list

def logic(gate_type, signals, gate_to_idx):
    symbol = get_gate_type(gate_type, gate_to_idx)
    if symbol == 'AND':  # AND
        for s in signals:
            if s == 0:
                return 0
        return 1

    elif symbol == 'NAND':  # NAND
        for s in signals:
            if s == 0:
                return 1
        return 0

    elif symbol == 'OR':  # OR
        for s in signals:
            if s == 1:
                return 1
        return 0

    elif symbol == 'NOR':  # NOR
        for s in signals:
            if s == 1:
                return 0
        return 1

    elif symbol == 'NOT':  # NOT
        for s in signals:
            if s == 1:
                return 0
            else:
                return 1

    elif symbol == 'BUFF':  # BUFF
     for s in signals:
         return s

    elif symbol == 'XOR':  # XOR
        z_count = 0
        o_count = 0
        for s in signals:
            if s == 0:
                z_count = z_count + 1
            elif s == 1:
                o_count = o_count + 1
        if z_count == len(signals) or o_count == len(signals):
            return 0
        return 1

    else:
        raise('Unsupport Gate Type: {:}'.format(gate_type))

def prob_logic(gate_type, signals, gate_to_idx):
    symbol = get_gate_type(gate_type, gate_to_idx)
    one = 0.0
    zero = 0.0

    if symbol == 'AND':  # AND
        mul = 1.0
        for s in signals:
            mul = mul * s[1]
        one = mul
        zero = 1.0 - mul

    elif symbol == 'NAND':  # NAND
        mul = 1.0
        for s in signals:
            mul = mul * s[1]
        zero = mul
        one = 1.0 - mul

    elif symbol == 'OR':  # OR
        mul = 1.0
        for s in signals:
            mul = mul * s[0]
        zero = mul
        one = 1.0 - mul

    elif symbol == 'NOR':  # NOR
        mul = 1.0
        for s in signals:
            mul = mul * s[0]
        one = mul
        zero = 1.0 - mul

    elif symbol == 'NOT':  # NOT
        for s in signals:
            one = s[0]
            zero = s[1]
    
    elif symbol == 'BUFF': # BUFF
        for s in signals:
            one = s[1]
            zero = s[0]

    elif symbol == 'XOR':  # XOR
        mul0 = 1.0
        mul1 = 1.0
        for s in signals:
            mul0 = mul0 * s[0]
        for s in signals:
            mul1 = mul1 * s[1]

        zero = mul0 + mul1
        one = 1.0 - zero

    else:
        raise('Unsupport Gate Type: {:}'.format(gate_type))

    return zero, one

def obs_prob(x, r, y, input_signals, gate_to_idx):
    symbol = get_gate_type(x[r][1], gate_to_idx)
    if symbol == 'AND' or symbol == 'NAND':
        obs = y[r]
        for s in input_signals:
            for s1 in input_signals:
                if s != s1:
                    obs = obs * x[s1][3]
            if obs < y[s] or y[s] == -1:
                y[s] = obs

    elif symbol == 'OR' or symbol == 'NOR':
        obs = y[r]
        for s in input_signals:
            for s1 in input_signals:
                if s != s1:
                    obs = obs * x[s1][4]
            if obs < y[s] or y[s] == -1:
                y[s] = obs

    elif symbol == 'NOT':
        obs = y[r]
        for s in input_signals:
            if obs < y[s] or y[s] == -1:
                y[s] = obs

    elif symbol == 'BUFF':
        obs = y[r]
        for s in input_signals:
            if obs < y[s] or y[s] == -1:
                y[s] = obs

    elif symbol == 'XOR':
        if len(input_signals) != 2:
            print('Not support non 2-input XOR Gate')
            raise
        # computing for a node
        obs = y[r]
        s = input_signals[1]
        if x[s][3] > x[s][4]:
            obs = obs * x[s][3]
        else:
            obs = obs * x[s][4]
        y[input_signals[0]] = obs

        # computing for b node
        obs = y[r]
        s = input_signals[0]
        if x[s][3] > x[s][4]:
            obs = obs * x[s][3]
        else:
            obs = obs * x[s][4]
        y[input_signals[1]] = obs

    else:
        raise('Unsupport Gate Type: {:}'.format(x[r][1]))

    return y

def random_pattern_generator(no_PIs):
    vector = [0] * no_PIs

    vector = randint(2, size=no_PIs)
    return vector

def feature_generation(x_data, edge_index_data):
    fanout_list = []
    fanin_list = []
    bfs_q = []
    x_data_level = [-1] * len(x_data)
    max_level = 0
    for idx, x_data_info in enumerate(x_data):
        fanout_list.append([])
        fanin_list.append([])
        if x_data_info[1] == 0:
            bfs_q.append(idx)
            x_data_level[idx] = 0
    for edge in edge_index_data:
        fanout_list[edge[0]].append(edge[1])
        fanin_list[edge[1]].append(edge[0])
    while len(bfs_q) > 0:
        idx = bfs_q[-1]
        bfs_q.pop()
        tmp_level = x_data_level[idx] + 1
        for next_node in fanout_list[idx]:
            if x_data_level[next_node] < tmp_level:
                x_data_level[next_node] = tmp_level
                bfs_q.insert(0, next_node)
                if x_data_level[next_node] > max_level:
                    max_level = x_data_level[next_node]
    level_list = []
    for level in range(max_level+1):
        level_list.append([])
    if -1 in x_data_level:
        print('Wrong')
        raise
    else:
        if max_level == 0:
            level_list = [[]]
        else:
            for idx in range(len(x_data)):
                x_data[idx].append(x_data_level[idx])
                level_list[x_data_level[idx]].append(idx)
    return x_data, edge_index_data, level_list, fanin_list, fanout_list

def generate_prob_cont(x_data, PI_indexes, level_list, fanin_list, gate_to_idx):
    '''
    Function to calculate Controlability values, i.e. C1 and C0 for the nodes.
    Modified by Zhengyuan, 27-09-2021
    ...
    Parameters:
        x_data : list(list((str, int, int))), the node feature matrix with shape [num_nodes, num_node_features], the current dimension of num_node_features is 3, wherein 0th - node_name defined in bench (str); 1st - integer index for the gate type; 2nd - logic level.
        PI_indexes : list(int), the indices for the primary inputs
        level_list: logic levels
        fanin_list: the fanin node indexes for each node
    Return:
        x_data : list(list((str, int, int))), the node feature matrix with shape [num_nodes, num_node_features], the current dimension of num_node_features is 3, wherein 0th - node_name defined in bench (str); 1st - integer index for the gate type; 2nd - logic level; 3rd - C1; 4th - C0.
    '''
    y = [0] * len(x_data)

    for i in PI_indexes:
        y[i] = [0.5, 0.5]

    for level in range(1, len(level_list), 1):
        for idx in level_list[level]:
            source_node = fanin_list[idx]
            source_signals = []
            for node in source_node:
                source_signals.append(y[node])
            if len(source_signals) > 0:
                zero, one = prob_logic(x_data[idx][1], source_signals, gate_to_idx)
                y[idx] = [zero, one]

    for i, prob in enumerate(y):
        x_data[i].append(prob[1])
        x_data[i].append(prob[0])

    return x_data

def generate_prob_obs(x_data, level_list, fanin_list, fanout_list, gate_to_idx):
    '''
        Function to calculate Observability values, i.e. CO.
        Modified by Zhengyuan, 27-09-2021
        ...
        Parameters:
            x_data : list(list((str, int, int))), the node feature matrix with shape [num_nodes, num_node_features], the current dimension of num_node_features is 3, wherein 0th - node_name defined in bench (str); 1st - integer index for the gate type; 2nd - logic level.
            level_list: logic levels
            fanin_list: the fanin node indexes for each node
            fanout_list: the fanout node indexes for each node
        Return:
            x_data : list(list((str, int, int))), the node feature matrix with shape [num_nodes, num_node_features], the current dimension of num_node_features is 3, wherein 0th - node_name defined in bench (str); 1st - integer index for the gate type; 2nd - logic level; 3rd - C1; 4th - C0; 5th - CO.
        '''
    # Array node into level_list

    y = [-1] * len(x_data)

    POs_indexes = []
    for idx, nxt in enumerate(fanout_list):
        if len(nxt) == 0:
            POs_indexes.append(idx)
            y[idx] = 1

    for level in range(len(level_list) - 1, -1, -1):
        for idx in level_list[level]:
            source_signals = fanin_list[idx]
            if len(source_signals) > 0:
                y = obs_prob(x_data, idx, y, source_signals, gate_to_idx)

    for i, val in enumerate(y):
        x_data[i].append(val)

    return x_data

def identify_reconvergence(x_data, level_list, fanin_list, fanout_list):
    '''
    Function to identify the reconvergence nodes in the given circuit.
    The algorithm is done under the principle that we only consider the minimum reconvergence structure.
    Modified by Zhengyuan 27-09-2021
    ...
    Parameters:
        x_data : list(list((str, int, int))), the node feature matrix with shape [num_nodes, num_node_features], the current dimension of num_node_features is 3, wherein 0th - node_name defined in bench (str); 1st - integer index for the gate type; 2nd - logic level; 3rd - C1, 4th - C0, 5th - Obs.
        level_list: logic levels
        fanin_list: the fanin node indexes for each node
        fanout_list: the fanout node indexes for each node
    Return:
        x_data : list(list((str, int, int))), the node feature matrix with shape [num_nodes, num_node_features], the current dimension of num_node_features is 3, wherein 0th - node_name defined in bench (str); 1st - integer index for the gate type; 2nd - logic level; 3rd - C1; 4th - C0; 5th - Obs; 6th - fan-out, 7th - boolean recovengence, 8th - index of the source node (-1 for non recovengence).
        rc_lst: list(int), the index for the reconvergence nodes
    '''
    for idx, node in enumerate(x_data):
        if len(fanout_list[idx]) > 1:
            x_data[idx].append(1)
        else:
            x_data[idx].append(0)

        # fanout list (FOL)
    FOL = []
    fanout_num = []
    is_del = []
    # RC (same as reconvergence_nodes)
    rc_lst = []
    max_level = 0
    for x_data_info in x_data:
        if x_data_info[2] > max_level:
            max_level = x_data_info[2]
        FOL.append([])
    for idx, x_data_info in enumerate(x_data):
        fanout_num.append(len(fanout_list[idx]))
        is_del.append(False)

    for level in range(max_level + 1):
        if level == 0:
            for idx in level_list[0]:
                x_data[idx].append(0)
                x_data[idx].append(-1)
                if x_data[idx][6]:
                    FOL[idx].append(idx)
        else:
            for idx in level_list[level]:
                FOL_tmp = []
                FOL_del_dup = []
                save_mem_list = []
                for pre_idx in fanin_list[idx]:
                    if is_del[pre_idx]:
                        print('[ERROR] This node FOL has been deleted to save memory')
                        raise
                    FOL_tmp += FOL[pre_idx]
                    fanout_num[pre_idx] -= 1
                    if fanout_num[pre_idx] == 0:
                        save_mem_list.append(pre_idx)
                for save_mem_idx in save_mem_list:
                    FOL[save_mem_idx].clear()
                    is_del[save_mem_idx] = True
                FOL_cnt_dist = Counter(FOL_tmp)
                source_node_idx = 0
                source_node_level = -1
                is_rc = False
                for dist_idx in FOL_cnt_dist:
                    FOL_del_dup.append(dist_idx)
                    if FOL_cnt_dist[dist_idx] > 1:
                        is_rc = True
                        if x_data[dist_idx][2] > source_node_level:
                            source_node_level = x_data[dist_idx][2]
                            source_node_idx = dist_idx
                if is_rc:
                    x_data[idx].append(1)
                    x_data[idx].append(source_node_idx)
                    rc_lst.append(idx)
                else:
                    x_data[idx].append(0)
                    x_data[idx].append(-1)

                FOL[idx] = FOL_del_dup
                if x_data[idx][6]:
                    FOL[idx].append(idx)
    del (FOL)

    return x_data, rc_lst

def backward_search(node_idx, fanin_list, x_data, min_level):
    if x_data[node_idx][2] <= min_level:
        return []
    result = []
    for pre_node in fanin_list[node_idx]:
        if pre_node not in result:
            l = [pre_node]
            res = backward_search(pre_node, fanin_list, x_data, min_level)
            result = result + l + list(set(res))
        else:
            l = [pre_node]
            result = result + l
    return result

def simulator(x_data, PI_indexes, level_list, fanin_list, num_patterns, gate_to_idx):
    y = [0] * len(x_data)
    y1 = [0] * len(x_data)
    pattern_count = 0
    no_of_patterns = min(num_patterns, 10 * pow(2, len(PI_indexes)))
    print('No of Patterns: {:}'.format(no_of_patterns))

    print('[INFO] Begin simulation')
    while pattern_count < no_of_patterns:
        input_vector = random_pattern_generator(len(PI_indexes))

        j = 0
        for i in PI_indexes:
            y[i] = input_vector[j]
            j = j + 1

        for level in range(1, len(level_list), 1):
            for node_idx in level_list[level]:
                source_signals = []
                for pre_idx in fanin_list[node_idx]:
                    source_signals.append(y[pre_idx])
                if len(source_signals) > 0:
                    gate_type = x_data[node_idx][1]
                    y[node_idx] = logic(gate_type, source_signals, gate_to_idx)
                    if y[node_idx] == 1:
                        y1[node_idx] = y1[node_idx] + 1

        pattern_count = pattern_count + 1
        if pattern_count % 10000 == 0:
            print("pattern count = {:}k".format(int(pattern_count / 1000)))

    for i, _ in enumerate(y1):
        y1[i] = [y1[i] / pattern_count]

    for i in PI_indexes:
        y1[i] = [0.5]

    return y1

def gen_mask(x_data, ori_mask):
    for idx, x_data_info in enumerate(x_data):
        x_data[idx].append(1)
    return x_data