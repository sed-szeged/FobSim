import random

network_waiting_times = {}


def generate_random_waiting_times(expected_chain_length, poet_block_time, object_name):
    dict_of_waiting_times = {0: 0}
    for i in range(2 * expected_chain_length):
        dict_of_waiting_times[i+1] = random.randint(0, 10 * poet_block_time)
    network_waiting_times[object_name] = dict_of_waiting_times
    return dict_of_waiting_times
