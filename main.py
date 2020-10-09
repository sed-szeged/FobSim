from multiprocessing import Process
import Fog
import end_user
import miner
import blockchain
import consensus
import random
import json
import os
import shutil
import mempool
import output
import time


with open("Sim_parameters.json") as json_file:
    data = json.load(json_file)

list_of_end_users = []
fogNodes = []
transactions_list = []
mining_processes = []
list_of_authorized_miners = []
blockchainFunction = 0
blockchainPlacement = 0
number_of_miner_neighbours = data["number_of_each_miner_neighbours"]
NumOfFogNodes = data["NumOfFogNodes"]
NumOfTaskPerUser = data["NumOfTaskPerUser"]
NumOfMiners = data["NumOfMiners"]
numOfTXperBlock = data["numOfTXperBlock"]
num_of_users_per_fog_node = data["num_of_users_per_fog_node"]
blockchain_functions = [1, 2, 3, 4]
blockchain_placement_options = [1, 2]


def user_input():
    for filename in os.listdir('temporary'):
        file_path = os.path.join('temporary', filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))
    with open('temporary/confirmation_log.json', 'w') as awards_log:
        json.dump({}, awards_log, indent=4)
    with open('temporary/miner_wallets_log.json', 'w') as miner_wallets_log:
        json.dump({}, miner_wallets_log, indent=4)
    while True:
        output.choose_functionality()
        global blockchainFunction
        blockchainFunction = int(input())
        if consensus.check_input(blockchainFunction, blockchain_functions):
            break
        else:
            print("Input is incorrect, try again..!")
    while True:
        output.choose_placement()
        global blockchainPlacement
        blockchainPlacement = int(input())
        if consensus.check_input(blockchainPlacement, blockchain_placement_options):
            break
        else:
            print("Input is incorrect, try again..!")


def initiate_network():
    for count in range(NumOfFogNodes):
        fogNodes.append(Fog.Fog(count + 1))
        for p in range(num_of_users_per_fog_node):
            list_of_end_users.append(end_user.User(p + 1, count+1))
    print("*****************\nEnd_users are up\nFog nodes are up\nEnd-Users are connected to their Fog nodes...\n")
    if blockchainFunction == 4:
        output.GDPR_warning()
        while True:
            print("If you don't want other attributes to be added to end_users, input: done\n")
            new_attribute = input("If you want other attributes to be added to end_users, input them next:\n")
            if new_attribute == 'done':
                break
            else:
                for user in list_of_end_users:
                    user.identity_added_attributes[new_attribute] = ''
                print("The network has " + str(len(list_of_end_users)) +
                      " end_users.\n For each of them, you need to input the value of newly added identity "
                      "attributes(if any)\n")
    for user in list_of_end_users:
        user.create_tasks(NumOfTaskPerUser, blockchainFunction, list_of_end_users)
        user.send_tasks(fogNodes)
        print("End_user " + str(user.addressParent) + "." + str(user.addressSelf) + " had sent its tasks to the fog layer")


def initiate_miners():
    the_miners_list = []
    miner_wallets_log_py = {}
    if blockchainPlacement == 1:
        for i in range(NumOfFogNodes):
            the_miners_list.append(miner.Miner(i + 1))
    if blockchainPlacement == 2:
        for i in range(NumOfMiners):
            the_miners_list.append(miner.Miner(i + 1))
    output.miners_are_up()
    for entity in the_miners_list:
        with open(str("temporary/" + entity.address + "_local_chain.json"), "w") as f:
            json.dump({}, f)
        with open("temporary/miner_wallets_log.json", 'w') as miner_wallets_log:
            miner_wallets_log_py[str(entity.address)] = data['miners_initial_wallet_value']
            json.dump(miner_wallets_log_py, miner_wallets_log, indent=4)
        while len(entity.neighbours) < number_of_miner_neighbours:
            neighbour = random.choice(the_miners_list).address
            if neighbour != entity.address:
                entity.neighbours.add(neighbour)
    return the_miners_list


def give_miners_authorization(the_miners_list, the_type_of_consensus):
    if the_type_of_consensus == 3:
        # automated approach:
        # for i in range(25):
        #     the_miners_list[i].isAuthorized = True
        #     list_of_authorized_miners.append(the_miners_list[i])

        # user input approach:
        output.authorization_trigger(blockchainPlacement, NumOfFogNodes, NumOfMiners)
        while True:
            authorized_miner = input()
            if authorized_miner == "done":
                break
            else:
                for node in the_miners_list:
                    if node.address == "Miner_" + authorized_miner:
                        node.isAuthorized = True
                        list_of_authorized_miners.append(node)


def initiate_genesis_block():
    genesis_transactions = ["genesis_block"]
    for i in range(len(miner_list)):
        genesis_transactions.append(miner_list[i].address)
    genesis_block = blockchain.generate_new_block(genesis_transactions, 'The Network', 0)
    output.block_info(genesis_block, type_of_consensus)
    for elem in miner_list:
        elem.receive_new_block(genesis_block, type_of_consensus, miner_list, blockchainFunction, mempool.discarded_txs)
    output.genesis_block_generation()


def send_tasks_to_BC():
    for node in fogNodes:
        node.send_tasks_to_BC()


def miners_trigger(the_miners_list, the_type_of_consensus):
    output.mempool_info(mempool.MemPool)
    while mempool.MemPool.qsize() > 0:
        if the_type_of_consensus == 1:
            for obj in the_miners_list:
                # non-parallel approach
                obj.build_block(numOfTXperBlock, mempool.MemPool, the_miners_list, the_type_of_consensus, blockchainFunction, mempool.discarded_txs)
                # parallel approach
            #     process = Process(target=obj.build_block, args=(numOfTXperBlock, mempool.MemPool, the_miners_list, the_type_of_consensus, blockchainFunction, mempool.discarded_txs, ))
            #     mining_processes.append(process)
            #     process.start()
            # for mining_process in mining_processes:
            #     mining_process.join()
        if the_type_of_consensus == 2:
            randomly_chosen_miners = []
            x = int(round((len(the_miners_list)/2), 0))
            for i in range(x):
                randomly_chosen_miners.append(random.choice(the_miners_list))
            biggest_stake = 0
            final_chosen_miner = the_miners_list[0]
            with open('temporary/miners_stake_amounts.json', 'r') as temp_file:
                temp_file_py = json.load(temp_file)
                for chosen_miner in randomly_chosen_miners:
                    if temp_file_py[chosen_miner.address] > biggest_stake:
                        biggest_stake = temp_file_py[chosen_miner.address]
                        final_chosen_miner = chosen_miner
                for entity in the_miners_list:
                    entity.next_pos_block_from = final_chosen_miner.address
                if mempool.MemPool.qsize() != 0:
                    final_chosen_miner.build_block(numOfTXperBlock, mempool.MemPool, the_miners_list, the_type_of_consensus, blockchainFunction, mempool.discarded_txs)
        if the_type_of_consensus == 3:
            for obj in miner_list:
                if mempool.MemPool.qsize() != 0:
                    obj.build_block(numOfTXperBlock, mempool.MemPool, the_miners_list, the_type_of_consensus, blockchainFunction, mempool.discarded_txs)


def inform_miners_of_users_wallets():
    if blockchainFunction == 3:
        user_wallets = {}
        for user in list_of_end_users:
            wallet_info = {'parent': user.addressParent,
                           'self': user.addressSelf,
                           'wallet_value': user.wallet}
            user_wallets[str(user.addressParent) + '.' + str(user.addressSelf)] = wallet_info
        for i in range(len(miner_list)):
            with open(str("temporary/" + miner_list[i].address + "_users_wallets.json"), "w") as f:
                json.dump(user_wallets, f, indent=4)


if __name__ == '__main__':
    user_input()
    initiate_network()
    type_of_consensus = consensus.choose_consensus()
    miner_list = initiate_miners()
    give_miners_authorization(miner_list, type_of_consensus)
    inform_miners_of_users_wallets()
    blockchain.stake(miner_list, type_of_consensus)
    initiate_genesis_block()
    send_tasks_to_BC()
    miners_trigger(miner_list, type_of_consensus)
    blockchain.award_winning_miners(len(miner_list))
    output.finish()
