import hashlib
import random
import output
import modification

data = modification.read_file("Sim_parameters.json")
diff = data["puzzle_difficulty"]
target = 2 ** (256 - diff)
list_of_stakes = [['Network', 0]]
mining_award = data["mining_award"]


def report_a_successful_block_addition(winning_miner, hash_of_added_block):
    record_exist = False
    temporary_confirmation_log = modification.read_file("temporary/confirmation_log.json")
    for key in temporary_confirmation_log:
        if key == hash_of_added_block and winning_miner == temporary_confirmation_log[key]['winning_miner']:
            temporary_confirmation_log[key]['votes'] += 1
            record_exist = True
            break
    if not record_exist:
        temporary_confirmation_log[str(hash_of_added_block)] = {'winning_miner': winning_miner, 'votes': 1}
    modification.rewrite_file("temporary/confirmation_log.json", temporary_confirmation_log)


def award_winning_miners(num_of_miners):
    final_confirmation_log = modification.read_file("temporary/confirmation_log.json")
    miner_final_wallets_log_py = modification.read_file("temporary/miner_wallets_log.json")
    for key in final_confirmation_log:
        if final_confirmation_log[key]['votes'] > int(num_of_miners/2):
            for key1 in miner_final_wallets_log_py:
                if key1 == final_confirmation_log[key]['winning_miner']:
                    miner_final_wallets_log_py[key1] += mining_award
    modification.rewrite_file("temporary/miner_wallets_log.json", miner_final_wallets_log_py)


def stake(list_of_miners, num_of_consensus):
    if num_of_consensus == 2:
        for miner in list_of_miners:
            temp_miner_wallets_log_py = modification.read_file('temporary/miner_wallets_log.json')
            temp_miners_stake_amounts_py = modification.read_file('temporary/miners_stake_amounts.json')
            temp_miners_stake_amounts_py[miner.address] = random.randint(0, temp_miner_wallets_log_py[miner.address])
            temp_miner_wallets_log_py[miner.address] -= temp_miners_stake_amounts_py[miner.address]
            modification.rewrite_file('temporary/miner_wallets_log.json', temp_miner_wallets_log_py)
            modification.rewrite_file('temporary/miners_stake_amounts.json', temp_miners_stake_amounts_py)


def fork_analysis(list_of_miners):
    chain_versions = []
    for entity in list_of_miners:
        temp_path = "temporary/" + entity.address + "_local_chain.json"
        chain = modification.read_file(temp_path)
        h = hashlib.sha256()
        h.update(str(chain).encode(encoding='UTF-8'))
        hashed_chain = h.hexdigest()
        if hashed_chain in chain_versions:
            pass
        else:
            chain_versions.append(hashed_chain)
    output.fork_analysis(len(chain_versions))
    modification.write_file('temporary/forking_log.json', {"Number of times a fork appeared": len(chain_versions) - 1})
