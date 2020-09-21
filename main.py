from multiprocessing import Process
import Fog
import end_user
import miner
import memPool
import blockchain
import consensus
import random
import json

with open("Sim_parameters.json") as json_file:
    data = json.load(json_file)
list_of_end_users = []
fogNodes = []
transactions_list = []
mining_processes = []
list_of_authorized_miners = []
blockchainFunction = 0
blockchainPlacement = 0
award_log = blockchain.AwardLog()
NumOfFogNodes = data["NumOfFogNodes"]
NumOfTaskPerUser = data["NumOfTaskPerUser"]
NumOfMiners = data["NumOfMiners"]
numOfTXperBlock = data["numOfTXperBlock"]
num_of_users_per_fog_node = data["num_of_users_per_fog_node"]


def user_input():
    print("Please choose the function of the Blockchain network:\n"
          "(1) Data Management\n"
          "(2) Computational services\n"
          "(3) Payment\n"
          "(4) Identity Management\n")
    global blockchainFunction
    blockchainFunction = int(input())
    print("Please choose the placement of the Blockchain network:\n"
          "(1) Fog Layer\n"
          "(2) End-User layer\n")
    global blockchainPlacement
    blockchainPlacement = int(input())


def initiate_network():
    for count in range(NumOfFogNodes):
        fogNodes.append(Fog.Fog(count + 1))
        for p in range(num_of_users_per_fog_node):
            list_of_end_users.append(end_user.User(p + 1, count+1))
    print("*****************End_users are up\nFog nodes are up\nEnd-Users are connected to their Fog nodes...\n")
    if blockchainFunction == 4:
        print("###########################################"
              "\nWARNING: Each end-user's address and the address of the fog component it is connected with,\n "
              "will be immutably saved on the chain. This is not a GDPR-compliant practice.\n"
              "if you need to have your application GDPR-compliant, you need to change the configuration,\n"
              " so that other types of identities be saved on the immutable chain, and re-run the simulation."
              "\n###########################################\n")
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


def deploy_miners_in_fog_nodes(the_miners_list, num_of_consensus):
    for i in range(NumOfFogNodes):
        the_miners_list.append(miner.Miner(i + 1))
    print("*****************\nMiner nodes are up and waiting for the genesis block...!\n")
    return the_miners_list


def deploy_miners_in_end_user_layer(the_miners_list, num_of_consensus):
    for i in range(NumOfMiners):
        the_miners_list.append(miner.Miner(i + 1))
    print("*****************\nMiner nodes are up and waiting for the genesis block...!\n")
    return the_miners_list


def initiate_miners(num_of_consensus):
    the_miners_list = []
    if blockchainPlacement == 1:
        the_miners_list = deploy_miners_in_fog_nodes(the_miners_list, num_of_consensus)
    if blockchainPlacement == 2:
        the_miners_list = deploy_miners_in_end_user_layer(the_miners_list, num_of_consensus)
    return the_miners_list


def give_miners_authorization(the_miners_list, type_of_consensus):
    if type_of_consensus == 3:
        # authomated approach:

        # for i in range(25):
        #     the_miners_list[i].isAuthorized = True
        #     list_of_authorized_miners.append(the_miners_list[i])

        # user input approach:

        print("please input the address of authorized:")
        if blockchainPlacement == 1:
            print("Fog Nodes")
        else:
            print("End-users")
        print("to generate new blocks in the exact following format:")
        print(">>>> 1 OR 3 OR 50 ... (up to: ")
        if blockchainPlacement == 1:
            print(str(NumOfFogNodes) + " fog nodes available")
        else:
            print(str(NumOfMiners) + " miners available in the EU layer")
        print("Once done, kindly input: done")
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
    genesis_block = blockchain.Block(genesis_transactions, 'The Network')
    for elem in miner_list:
        elem.receive_new_block(memPool.MemPool, genesis_block, type_of_consensus, miner_list, blockchainFunction,
                               list_of_end_users, award_log)
    print("\nGenesis Block is generated. The Blockchain system is up...!\nMiners will now collect transactions from "
          "memPool and start building blocks...\n\n")
    print("The following block has been proposed by " + genesis_block.generator_id +
          " and is generated into the Blockchain network")
    print("**************************")
    print("transactions:")
    print(genesis_block.transactions)
    print("hash:")
    print(genesis_block.hash)
    print("timestamp:")
    print(genesis_block.timestamp)
    print("nonce:")
    print(genesis_block.nonce)
    print("previous_hash:")
    print(genesis_block.previous_hash)
    print("**************************")


def send_tasks_to_BC():
    print("mempool contents:")
    for node in fogNodes:
        node.send_tasks_to_BC()


def miners_trigger(the_miners_list, the_type_of_consensus):
    while memPool.MemPool.qsize() != 0:
        if the_type_of_consensus == 1:
            for obj in miner_list:
            ## non-parallel approach
                obj.build_block(numOfTXperBlock, memPool.MemPool, the_miners_list, the_type_of_consensus, list_of_end_users, blockchainFunction, award_log)
            ## parallel approach
            #     process = Process(target=obj.build_block,
            #                       args=(numOfTXperBlock, memPool.MemPool, the_miners_list, the_type_of_consensus, list_of_end_users, blockchainFunction, award_log, ))
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
            for chosen_miner in randomly_chosen_miners:
                if blockchain.read_the_stake(chosen_miner.address) > biggest_stake:
                    biggest_stake = blockchain.read_the_stake(chosen_miner.address)
                    final_chosen_miner = chosen_miner
            for entity in the_miners_list:
                entity.next_pos_block_from = final_chosen_miner.address
            final_chosen_miner.build_block(numOfTXperBlock, memPool.MemPool, the_miners_list, the_type_of_consensus, list_of_end_users, blockchainFunction, award_log)
        if the_type_of_consensus == 3:
            for obj in miner_list:
                obj.build_block(numOfTXperBlock, memPool.MemPool, the_miners_list, the_type_of_consensus, list_of_end_users, blockchainFunction, award_log)


def inform_miners_of_users_wallets():
    if blockchainFunction == 3:
        user_wallets = []
        for user in list_of_end_users:
            wallet_info = [user.addressParent, user.addressSelf, user.wallet]
            user_wallets.append(wallet_info)
            for i in range(len(miner_list)):
                with open(str("temporary/" + miner_list[i].address + "_users_wallets.json"), "w") as f:
                    json.dump(user_wallets, f)


def finish(miners):
    print("simulation is done. Do you want to check if all chains are the same? (y/n)")
    choose = input()
    if choose == 'y' or choose == 'Y':
        for entity in miners:
            entity.print_miner_local_chain()
        print("The wallets of miner nodes contain the following amounts: ")
        for entity in miners:
            print(str(entity.address) + " : " + str(entity.wallet))
    else:
        print("thank YOU..!")


if __name__ == '__main__':
    user_input()
    initiate_network()
    type_of_consensus = consensus.choose_consensus()
    miner_list = initiate_miners(type_of_consensus)
    give_miners_authorization(miner_list, type_of_consensus)
    inform_miners_of_users_wallets()
    consensus.pos_miners_staking(miner_list)
    initiate_genesis_block()
    send_tasks_to_BC()
    miners_trigger(miner_list, type_of_consensus)
    award_log.declare_winning_miners(len(miner_list))
    award_log.award_winning_miners(miner_list)
    finish(miner_list)

