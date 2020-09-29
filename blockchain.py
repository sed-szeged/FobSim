import time
import hashlib
import json
import os
import random

with open("Sim_parameters.json") as json_file:
    data = json.load(json_file)
diff = data["puzzle_difficulty"]
target = 2 ** (256 - diff)
list_of_stakes = [['Network', 0]]
mining_award = data["mining_award"]


def generate_new_block(transactions, generator_id, previous_hash):
    new_block = {'transactions': transactions,
                 'blockNo': 0,
                 'nonce': 0,
                 'generator_id': generator_id,
                 'previous_hash': previous_hash,
                 'timestamp': time.ctime(),
                 'hash': 0}
    new_block['hash'] = hashing_function(new_block['nonce'], new_block['transactions'], new_block['generator_id'], new_block['previous_hash'])
    return new_block


def hashing_function(nonce, transactions, generator_id, previous_hash):
    h = hashlib.sha256()
    h.update(str(nonce).encode(encoding='UTF-8') + str(transactions).encode(encoding='UTF-8')
             + str(generator_id).encode(encoding='UTF-8') + str(previous_hash).encode(encoding='UTF-8'))
    return h.hexdigest()


def report_a_successful_block_addition(winning_miner, hash_of_added_block):
    record_exist = False
    with open("temporary/confirmation_log.json", 'r') as f:
        temporary_confirmation_log = json.load(f)
    for key in temporary_confirmation_log:
        if key == hash_of_added_block and winning_miner == temporary_confirmation_log[key]['winning_miner']:
            temporary_confirmation_log[key]['votes'] += 1
            record_exist = True
            break
    if not record_exist:
        temporary_confirmation_log[str(hash_of_added_block)] = {'winning_miner': winning_miner, 'votes': 1}
    os.remove(str("temporary/confirmation_log.json"))
    with open(str("temporary/confirmation_log.json"), "w") as f:
        json.dump(temporary_confirmation_log, f, indent=4)


def award_winning_miners(list_of_miner_nodes):
    with open(str("temporary/confirmation_log.json"), 'r') as f:
        final_confirmation_log = json.load(f)
    with open("temporary/miner_wallets_log.json", 'r') as miner_final_wallets_log:
        miner_final_wallets_log_py = json.load(miner_final_wallets_log)
    for key in final_confirmation_log:
        if final_confirmation_log[key]['votes'] > int(len(list_of_miner_nodes)/2):
            for miner in list_of_miner_nodes:
                if miner.address == final_confirmation_log[key]['winning_miner']:
                    miner_final_wallets_log_py[str(miner.address)] += mining_award
    with open(str("temporary/miner_wallets_log.json"), "w") as f:
        json.dump(miner_final_wallets_log_py, f, indent=4)


def txs_back_to_memp(returned_transactions, mem_pool):
    for i in range(len(returned_transactions)):
        mem_pool.put(returned_transactions[i])


def stake(list_of_miners, num_of_consensus):
    if num_of_consensus == 2:
        for miner in list_of_miners:
            with open('temporary/miner_wallets_log.json', 'r') as x:
                temp_miner_wallets_log_py = json.load(x)
                with open('temporary/miners_stake_amounts.json', 'r') as y:
                    temp_miners_stake_amounts_py = json.load(y)
                    temp_miners_stake_amounts_py[miner.address] = random.randint(0, temp_miner_wallets_log_py[miner.address])
                    temp_miner_wallets_log_py[miner.address] -= temp_miners_stake_amounts_py[miner.address]
            os.remove('temporary/miner_wallets_log.json')
            os.remove('temporary/miners_stake_amounts.json')
            with open('temporary/miner_wallets_log.json', "w") as f:
                json.dump(temp_miner_wallets_log_py, f, indent=4)
            with open('temporary/miners_stake_amounts.json', "w") as f:
                json.dump(temp_miners_stake_amounts_py, f, indent=4)
