import Fog
import end_user
import miner
import blockchain
import random
import output
from math import ceil
import time
import modification
import new_consensus_module


data = modification.read_file("Sim_parameters.json")
list_of_end_users = []
fogNodes = []
transactions_list = []
list_of_authorized_miners = []
blockchainFunction = 0
blockchainPlacement = 0
number_of_miner_neighbours = data["number_of_each_miner_neighbours"]
NumOfFogNodes = data["NumOfFogNodes"]
NumOfTaskPerUser = data["NumOfTaskPerUser"]
NumOfMiners = data["NumOfMiners"]
numOfTXperBlock = data["numOfTXperBlock"]
num_of_users_per_fog_node = data["num_of_users_per_fog_node"]
blockchain_functions = ['1', '2', '3', '4']
blockchain_placement_options = ['1', '2']
expected_chain_length = ceil((num_of_users_per_fog_node * NumOfTaskPerUser * NumOfFogNodes) / numOfTXperBlock)
gossip_activated = data["Gossip_Activated"]
Automatic_PoA_miners_authorization = data["Automatic_PoA_miners_authorization?"]
Parallel_PoW_mining = data["Parallel_PoW_mining?"]
trans_delay = 0
delay_between_fog_nodes = data["delay_between_fog_nodes"]
delay_between_end_users = data["delay_between_end_users"]
poet_block_time = data['poet_block_time']
Asymmetric_key_length = data['Asymmetric_key_length']


def user_input():
    modification.initiate_files(gossip_activated)
    choose_functionality()
    choose_placement()


def choose_functionality():
    while True:
        output.choose_functionality()
        global blockchainFunction
        blockchainFunction = input()
        if blockchainFunction in blockchain_functions:
            blockchainFunction = int(blockchainFunction)
            break
        else:
            print("Input is incorrect, try again..!")


def choose_placement():
    while True:
        output.choose_placement()
        global blockchainPlacement
        blockchainPlacement = input()
        if blockchainPlacement in blockchain_placement_options:
            blockchainPlacement = int(blockchainPlacement)
            break
        else:
            print("Input is incorrect, try again..!")


def initiate_network():
    for count in range(NumOfFogNodes):
        fogNodes.append(Fog.Fog(count + 1))
        for p in range(num_of_users_per_fog_node):
            list_of_end_users.append(end_user.User(p + 1, count + 1))
    output.users_and_fogs_are_up()
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
                output.user_identity_addition_reminder(len(list_of_end_users))
    for user in list_of_end_users:
        user.create_tasks(NumOfTaskPerUser, blockchainFunction, list_of_end_users)
        user.send_tasks(fogNodes)
        print("End_user " + str(user.addressParent) + "." + str(user.addressSelf) + " had sent its tasks to the fog layer")


def initiate_miners():
    the_miners_list = []

    if blockchainPlacement == 1:
        for i in range(NumOfFogNodes):
            the_miners_list.append(miner.Miner(i + 1, trans_delay, gossip_activated))
    if blockchainPlacement == 2:
        for i in range(NumOfMiners):
            the_miners_list.append(miner.Miner(i + 1, trans_delay, gossip_activated))
    for entity in the_miners_list:
        modification.write_file("temporary/" + entity.address + "_local_chain.json", {})
        miner_wallets_log_py = modification.read_file("temporary/miner_wallets_log.json")
        miner_wallets_log_py[str(entity.address)] = data['miners_initial_wallet_value']
        modification.rewrite_file("temporary/miner_wallets_log.json", miner_wallets_log_py)
    print('Miners have been initiated..')
    connect_miners(the_miners_list)
    output.miners_are_up()
    return the_miners_list


def define_trans_delay(layer):
    transmission_delay = 0
    if layer == 1:
        transmission_delay = delay_between_fog_nodes
    if layer == 2:
        transmission_delay = delay_between_end_users
    return transmission_delay


def connect_miners(miners_list):
    print("Miners will be connected in a P2P fashion now. Hold on...")
    bridges = set()
    all_components = create_components(miners_list)
    for comp in all_components:
        bridge = random.choice(tuple(comp))
        bridges.add(bridge)
    bridging(bridges, miners_list)


def bridging(bridges, miners_list):
    while len(bridges) != 1:
        bridge = random.choice(tuple(bridges))
        other_bridge = random.choice(tuple(bridges))
        same_bridge = True
        while same_bridge:
            other_bridge = random.choice(tuple(bridges))
            if other_bridge != bridge:
                same_bridge = False
        for entity in miners_list:
            if entity.address == bridge:
                entity.neighbours.add(other_bridge)
            if entity.address == other_bridge:
                entity.neighbours.add(bridge)
        bridges.remove(bridge)


def create_components(miners_list):
    all_components = set()
    for entity in miners_list:
        component = set()
        while len(entity.neighbours) < number_of_miner_neighbours:
            neighbour = random.choice(miners_list).address
            if neighbour != entity.address:
                entity.neighbours.add(neighbour)
                component.add(neighbour)
                for entity_2 in miners_list:
                    if entity_2.address == neighbour:
                        entity_2.neighbours.add(entity.address)
                        component.add(entity.address)
                        break
        if component:
            all_components.add(tuple(component))
    return all_components


def give_miners_authorization(the_miners_list, the_type_of_consensus):
    if the_type_of_consensus == 3:
        # automated approach:
        if Automatic_PoA_miners_authorization:
            for i in range(len(the_miners_list)):
                the_miners_list[i].isAuthorized = True
                list_of_authorized_miners.append(the_miners_list[i])
        else:
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
    genesis_block = new_consensus_module.generate_new_block(genesis_transactions, 'The Network', 0, type_of_consensus)
    output.block_info(genesis_block, type_of_consensus)
    for elem in miner_list:
        elem.receive_new_block(genesis_block, type_of_consensus, miner_list, blockchainFunction, expected_chain_length)
    output.genesis_block_generation()


def send_tasks_to_BC():
    for node in fogNodes:
        node.send_tasks_to_BC()


def inform_miners_of_users_wallets():
    if blockchainFunction == 3:
        user_wallets = {}
        for user in list_of_end_users:
            wallet_info = {'parent': user.addressParent,
                           'self': user.addressSelf,
                           'wallet_value': user.wallet}
            user_wallets[str(user.addressParent) + '.' + str(user.addressSelf)] = wallet_info
        for i in range(len(miner_list)):
            modification.rewrite_file(str("temporary/" + miner_list[i].address + "_users_wallets.json"), user_wallets)


if __name__ == '__main__':
    user_input()
    initiate_network()
    type_of_consensus = new_consensus_module.choose_consensus()
    trans_delay = define_trans_delay(blockchainPlacement)
    miner_list = initiate_miners()
    give_miners_authorization(miner_list, type_of_consensus)
    inform_miners_of_users_wallets()
    blockchain.stake(miner_list, type_of_consensus)
    initiate_genesis_block()
    send_tasks_to_BC()
    time_start = time.time()
    if blockchainFunction == 2:
        expected_chain_length = ceil((num_of_users_per_fog_node * NumOfTaskPerUser * NumOfFogNodes))
    new_consensus_module.miners_trigger(miner_list, type_of_consensus, expected_chain_length, Parallel_PoW_mining, numOfTXperBlock, blockchainFunction, poet_block_time, Asymmetric_key_length)
    blockchain.award_winning_miners(len(miner_list))
    blockchain.fork_analysis(miner_list)
    output.finish()
    elapsed_time = time.time() - time_start
    print("elapsed time = " + str(elapsed_time) + " seconds")

