import blockchain
import mempool
import output
import modification
import random
from multiprocessing import Process
import encryption_module
import time
import PoET_server

# NON-MODIFIABLE PART:

num_of_consensus = 0


def choose_consensus():
    while True:
        output.choose_consensus(blockchain_CAs)
        global num_of_consensus
        num_of_consensus = input()
        if num_of_consensus in blockchain_CAs:
            num_of_consensus = int(num_of_consensus)
            prepare_necessary_files()
            break
        else:
            print("Input is incorrect, try again..!")
    return num_of_consensus


def trigger_pow_miners(the_miners_list, the_type_of_consensus, expected_chain_length, Parallel_PoW_mining,
                       numOfTXperBlock, blockchainFunction):
    mining_processes = []
    for counter in range(expected_chain_length):
        obj = random.choice(the_miners_list)
        if Parallel_PoW_mining:
            # parallel approach
            process = Process(target=obj.build_block, args=(
                numOfTXperBlock, mempool.MemPool, the_miners_list, the_type_of_consensus, blockchainFunction,
                expected_chain_length,))
            process.start()
            mining_processes.append(process)
        else:
            # non-parallel approach
            obj.build_block(numOfTXperBlock, mempool.MemPool, the_miners_list, the_type_of_consensus,
                            blockchainFunction, expected_chain_length)
        output.simulation_progress(counter, expected_chain_length)
    for process in mining_processes:
        process.join()


def trigger_pos_miners(the_miners_list, the_type_of_consensus, expected_chain_length, numOfTXperBlock,
                       blockchainFunction):
    for counter in range(expected_chain_length):
        randomly_chosen_miners = []
        x = int(round((len(the_miners_list) / 2), 0))
        for i in range(x):
            randomly_chosen_miners.append(random.choice(the_miners_list))
        biggest_stake = 0
        final_chosen_miner = the_miners_list[0]
        temp_file_py = modification.read_file('temporary/miners_stake_amounts.json')
        for chosen_miner in randomly_chosen_miners:
            stake = temp_file_py[chosen_miner.address]
            if stake > biggest_stake:
                biggest_stake = stake
                final_chosen_miner = chosen_miner
        for entity in the_miners_list:
            entity.next_pos_block_from = final_chosen_miner.address
        if mempool.MemPool.qsize() != 0:
            final_chosen_miner.build_block(numOfTXperBlock, mempool.MemPool, the_miners_list, the_type_of_consensus,
                                           blockchainFunction, expected_chain_length)
        output.simulation_progress(counter, expected_chain_length)


def trigger_poa_miners(the_miners_list, the_type_of_consensus, expected_chain_length, numOfTXperBlock,
                       blockchainFunction):
    for counter in range(expected_chain_length):
        for obj in the_miners_list:
            if mempool.MemPool.qsize() != 0:
                obj.build_block(numOfTXperBlock, mempool.MemPool, the_miners_list, the_type_of_consensus,
                                blockchainFunction, expected_chain_length)
        output.simulation_progress(counter, expected_chain_length)


def trigger_poet_miners(expected_chain_length, the_miners_list, poet_block_time, numOfTXperBlock, the_type_of_consensus, blockchainFunction, Asymmetric_key_length, Parallel_PoW_mining):
    for obj in the_miners_list:
        obj.waiting_times = PoET_server.generate_random_waiting_times(expected_chain_length, poet_block_time, obj.address)
        private_key, public_key = encryption_module.generate_PKI_keys(Asymmetric_key_length, obj.address+'_key')
    mining_processes = []
    for counter in range(expected_chain_length):
        least_waiting_time = poet_block_time + 1
        least_waiting_time_for = []
        for obj in the_miners_list:
            if PoET_server.network_waiting_times[obj.address][counter + 1] <= least_waiting_time:
                least_waiting_time = PoET_server.network_waiting_times[obj.address][counter + 1]
                least_waiting_time_for.append(obj.address)
        time.sleep(least_waiting_time)
        if Parallel_PoW_mining:
            # parallel approach
            for obj in the_miners_list:
                if obj.address in least_waiting_time_for:
                    process = Process(target=obj.build_block, args=(
                        numOfTXperBlock, mempool.MemPool, the_miners_list, the_type_of_consensus, blockchainFunction,
                        expected_chain_length,))
                    process.start()
                    mining_processes.append(process)
            for process in mining_processes:
                process.join()
        else:
            for obj in the_miners_list:
                if obj.address in least_waiting_time_for:
                    obj.build_block(numOfTXperBlock, mempool.MemPool, the_miners_list, the_type_of_consensus, blockchainFunction,
                                    expected_chain_length)


def pow_mining(block):
    while True:
        block['Header']['hash'] = encryption_module.hashing_function(block['Body'])
        if int(block['Header']['hash'], 16) > blockchain.target:
            block['Body']['nonce'] += 1
        else:
            break
    return block


def pow_block_is_valid(block, expected_previous_hash):
    condition_1 = block['Header']['hash'] == encryption_module.hashing_function(block['Body'])
    condition_2 = int(block['Header']['hash'], 16) <= blockchain.target
    condition_3 = block['Body']['previous_hash'] == expected_previous_hash
    if condition_1 and condition_2 and condition_3:
        return True
    return False


def pos_block_is_valid(generator_id, next_block_from, block, expected_previous_hash):
    condition_1 = block['Header']['hash'] == encryption_module.hashing_function(block['Body'])
    condition_2 = block['Body']['previous_hash'] == expected_previous_hash
    condition_3 = generator_id == next_block_from
    if condition_1 and condition_2 and condition_3:
        return True
    return False


def poa_block_is_valid(block, expected_previous_hash, miner_list):
    condition_1 = block['Body']['previous_hash'] == expected_previous_hash
    condition_2 = block['Header']['hash'] == encryption_module.hashing_function(block['Body'])
    if condition_1 and condition_2:
        for obj in miner_list:
            if obj.address == block['Header']['generator_id']:
                return obj.isAuthorized
    return False


def poet_block_is_valid(top_block, new_block):
    try:
        expected_block_poet = encryption_module.retrieve_signature_from_saved_key(top_block['Header']['hash'], new_block['Header']['generator_id'])
        condition1 = new_block['Header']['PoET'] == expected_block_poet
        condition2 = new_block['Header']['hash'] == encryption_module.hashing_function(new_block['Body'])
        condition3 = time.time() >= (top_block['Body']['timestamp'] + PoET_server.network_waiting_times[new_block['Header']['generator_id']][top_block['Header']['blockNo'] + 1])
        if condition1 and condition2 and condition3:
            return True
    except Exception as e:
        pass
    return False


# MODIFIABLE PART:
# 1- add a number and a name of the new consensus algorithm (all strings)
# to the 'blockchain_CAs' dictionary:


blockchain_CAs = {'1': 'Proof of Work (PoW)',
                  '2': 'Proof of Stake (PoS)',
                  '3': 'Proof of Authority (PoA)',
                  '4': 'Proof of Elapsed Time (PoET)',
                  '5': 'Example New CA'}

# 2-if your consensus algorithm requires other files to refer to while miners are
# processing TXs and Blocks, add them to the
# "prepare_necessry_files" function. Check the 'modification.py' file in this
# project to utilize already implemented functions


def prepare_necessary_files():
    if num_of_consensus == 2:
        modification.write_file('temporary/miners_stake_amounts.json', {})
    if num_of_consensus == 5:
        pass
        # modification.write_file('temporary/example_of_new_log_file.json', {})


# 3- the 'generate_new_block' generates a standard-like block. You can add more attributes
# to your new consensus blocks by adding an IF statement to this function:

def generate_new_block(transactions, generator_id, previous_hash, type_of_consensus):
    new_block = {'Header': {'generator_id': generator_id,
                            'hash': '',
                            'blockNo': 0},
                 'Body': {'transactions': transactions,
                          'nonce': 0,
                          'previous_hash': previous_hash,
                          'timestamp': time.time()}}
    if type_of_consensus == 1:
        new_block = pow_mining(new_block)
    else:
        new_block['Header']['hash'] = encryption_module.hashing_function(new_block['Body'])
    if type_of_consensus == 4:
        new_block['Header']['PoET'] = ''
    if type_of_consensus == 5:
        new_block['Header']['dummy_new_proof'] = dummy_proof_generator_function(new_block)
    return new_block

# 4- the 'miners_trigger' function triggers the miners to start mining/minting new blocks.
# add an IF statement to this function so that the simulator would know the trigger reference:


def miners_trigger(the_miners_list, the_type_of_consensus, expected_chain_length, Parallel_PoW_mining, numOfTXperBlock, blockchainFunction, poet_block_time, Asymmetric_key_length):
    output.mempool_info(mempool.MemPool)
    if the_type_of_consensus == 1:
        trigger_pow_miners(the_miners_list, the_type_of_consensus, expected_chain_length, Parallel_PoW_mining, numOfTXperBlock, blockchainFunction)
    if the_type_of_consensus == 2:
        trigger_pos_miners(the_miners_list, the_type_of_consensus, expected_chain_length, numOfTXperBlock, blockchainFunction)
    if the_type_of_consensus == 3:
        trigger_poa_miners(the_miners_list, the_type_of_consensus, expected_chain_length, numOfTXperBlock, blockchainFunction)
    if the_type_of_consensus == 4:
        trigger_poet_miners(expected_chain_length, the_miners_list, poet_block_time, numOfTXperBlock, the_type_of_consensus, blockchainFunction, Asymmetric_key_length, Parallel_PoW_mining)
    if the_type_of_consensus == 5:
        trigger_dummy_miners(the_miners_list, numOfTXperBlock, the_type_of_consensus, blockchainFunction, expected_chain_length)

# 5- Add miner selection strategy here in a trigger_miners function as follows. The Selection strategy can be
# randomized (as non-parallel PoW), conditioned (as PoS), parallel-randomized (as PoW), FCFS (as PoA), etc.
# You can also modify the termination strategy here according to the application of your consensus and the simulation scenarios
# you would like to emulate.
# In the example below, miner selection strategy is Randomized, and the simulation will terminate once all TXs are processed.


def trigger_dummy_miners(the_miners_list, numOfTXperBlock, the_type_of_consensus, blockchainFunction, expected_chain_length):
    counter = -1
    while mempool.MemPool.qsize() != 0:
        obj = random.choice(the_miners_list)
        obj.build_block(numOfTXperBlock, mempool.MemPool, the_miners_list, the_type_of_consensus, blockchainFunction, expected_chain_length)
        counter += 1
    output.simulation_progress(counter, expected_chain_length)


# 6- the 'block_is_valid' function is used by the miners to validate data within the received blocks.
# add an IF statement to this function so that the simulator would know the validation function to refer to:

def block_is_valid(type_of_consensus, new_block, top_block, next_pos_block_from, miner_list):
    if type_of_consensus == 1:
        return pow_block_is_valid(new_block, top_block['Header']['hash'])
    if type_of_consensus == 2:
        return pos_block_is_valid(new_block['Header']['generator_id'], next_pos_block_from, new_block, top_block['Header']['hash'])
    if type_of_consensus == 3:
        return poa_block_is_valid(new_block, top_block['Header']['hash'], miner_list)
    if type_of_consensus == 4:
        return poet_block_is_valid(top_block, new_block)
    if type_of_consensus == 5:
        return dummy_block_is_valid(new_block)


# 7- Add miner validation strategy in a 'block_is_valid' function (must match the name specified
# in the 'block_is_valid' function). The function MUST return either True or False.
# The parameters passed to this function differ depending on a) the application of the consensus, and b) the validation criteria.
# to see some examples, refer to the 'block_is_valid' functions in the NON-MODIFIABLE area above^^^^^^.
# Preferred approach to implement this function is to define the conditions to check. If all conditions were met,
# the function would return true. Otherwise it shall return False. Note that this is a Proof-based consensus approach.
# If other approach is to be implemented (e.g. PBFT), other functions and related variables need to be added/modified
# in the 'miner.py' file in this project.

def dummy_block_is_valid(block):
    return block['Header']['dummy_new_proof'] == encryption_module.hashing_function(block['Body'])

# 8- Add other type of proof that could be validated by the 'block_is_valid' function.
# To do that, you can implement a function that generates the proof as in the
# 'pow_mining' function in the NON-MODIFIABLE area above^^^^^^. Once implemented, the
# 'block_is_valid' function must be modified accordingly so that valid blocks only are added.


def dummy_proof_generator_function(block):
    return encryption_module.hashing_function(block['Body'])
