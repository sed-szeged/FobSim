def genesis_block_generation():
    print("\nGenesis Block is generated. The Blockchain system is up...!")
    print("Miners will now collect transactions from memPool and start building blocks...\n\n")


def block_info(block, consensus_algorithm):
    print("The following block has been proposed by " + block['Header']['generator_id'] +
          " and is generated into the Blockchain network")
    print("**************************")
    print("transactions:")
    print(block['Body']['transactions'])
    print("hash:")
    print(block['Header']['hash'])
    print("timestamp:")
    print(block['Body']['timestamp'])
    if consensus_algorithm == 1:
        print("nonce:")
        print(block['Body']['nonce'])
    print("previous_hash:")
    print(block['Body']['previous_hash'])
    print("**************************")


def block_success_addition(self_address, generator_id):
    print("*******************************************")
    print(f"the block is now added to the local chain of {self_address}")
    if generator_id != self_address:
        print(f"this block was received from {generator_id}")
        print("##############################\n")


def AI_assisted_mining_wanted():
    print("Would you like to simulate AI-assisted mining along with the classical PoW mining (input Y/y to agree or N/n to discard)?\n")
    while True:
        try:
            decision = input()
            if decision in ['Y', 'y']:
                wanted = True
                break
            elif decision in ['N', 'n']:
                wanted = False
                break
            else:
                print('Your input is incorrect, please try again:\n')
        except Exception as e:
            print(e)
    if wanted:
        print(
            "Input the portion of miners (percentage out of all active) that should run this mining type (input 1--100)?\n")
        while True:
            try:
                portion = input()
                float_portion = int(portion) / 100
                break
            except Exception as e:
                print(e)
                print('Seems your input is incorrect, please try again:\n')
    else:
        float_portion = None
    return wanted, float_portion


def inform_of_fog_procedure(blockchain_function, stor_plc):
    if blockchain_function == 1:
        if stor_plc == 1:
            print('Tasks will be handled by the Blockchain')
        else:
            print('Tasks will be handled by the Fog Layer')
    if blockchain_function == 2:
        print('Tasks with +/- operations will be processed and stored by the Fog Layer. Rest will be processed and stored by the Blockchain')
    if blockchain_function == 3:
        print('All payment tasks will be handled by the Blockchain')
    if blockchain_function == 4:
        print('All Identity data will be stored only in the Fog Layer')
    confirm = input('Press Enter to proceed or Exit and modify on the SimParameters.json file.')


def simulation_progress(current_chain_length, expected_chain_length):
    # print("The simulation have passed " + str(100*((current_chain_length+1)/expected_chain_length)) + "% of TXs to miners")
    # print("Miners will mint new valid blocks and generate them to The BC network")
    pass


def fork_analysis(number_of_forks):
    if number_of_forks == 1:
        print("\n##############################\nThere were no forks during this run\n#############################\n")
    else:
        print("\n##############################\nAs the simulation is finished, " + str(number_of_forks) + " different versions of chains were found\n#############################\n")


def mempool_info(mempool):
    print('mempool contains the following TXs:')
    txs = [mempool.get() for _ in range(mempool.qsize())]
    for tx in txs:
        print(tx)
        mempool.put(tx)


def authorization_trigger(blockchain_placement, no_fogs, no_miners):
    print("please input the address of authorized:")
    if blockchain_placement == 1:
        print("Fog Nodes")
    else:
        print("End-users")
    print("to generate new blocks in the exact following format:")
    print(">>>> 1 OR 3 OR 50 ... (up to: ")
    if blockchain_placement == 1:
        print(f"{str(no_fogs)} fog nodes available")
    else:
        print(f"{str(no_miners)} miners available in the EU layer")
    print("Once done, kindly input: done")


def choose_functionality():
    print("Please choose the function of the Blockchain network:\n"
          "(1) Data Management\n"
          "(2) Computational services\n"
          "(3) Payment\n"
          "(4) Identity Management\n")


def choose_placement():
    print("Please choose the placement of the Blockchain network:\n"
          "(1) Fog Layer\n"
          "(2) End-User layer\n")


def choose_consensus(dict_of_consensus_algos):
    print("\nPlease choose the Consensus algorithm to be used in the simulation:\n")
    for key in dict_of_consensus_algos:
        print(f'{key}: {dict_of_consensus_algos[key]}')


def txs_success(txs_per_user, parent_add, self_add):
    print(f"{str(txs_per_user)} data records had been generated by End-User no. {str(parent_add)}.{str(self_add)}")


def GDPR_warning():
    print("###########################################"
          "\nWARNING: Each end-user's address and the address of the fog component it is connected with,\n "
          "will be immutably saved on the chain. This is not a GDPR-compliant practice.\n"
          "if you need to have your application GDPR-compliant, you need to change the configuration,\n"
          " so that other types of identities be saved on the immutable chain, and re-run the simulation."
          "\n###########################################\n")


def miners_are_up():
    print("*****************\nMiner nodes are up, connected to their neighbors, and waiting for the genesis block...!\n")


def illegal_tx(tx, wallet_content):
    print("the following transaction is illegal:")
    print(tx)
    print(f"the end_user_wallet contains only {str(wallet_content)} digital coins..!")

    print("the transaction is withdrawn from the block")


def illegal_block():
    print("The proposed block is not valid."
          "\nTransactions will be sent back to the mempool and mined again..!")


def unauthorized_miner_msg(miner_address):
    print(f"Miner: {miner_address} is not authorized to generate a new block..!")


def block_discarded():
    print("The received block was ignored because it is already in the local chain")


def users_and_fogs_are_up():
    print("*****************\nEnd_users are up\nFog nodes are up\nEnd-Users are connected to their Fog nodes...\n")


def user_identity_addition_reminder(Num_endusers):
    print((f"The network has {str(Num_endusers)}" + " end_users.\n For each of them, you need to input the value of newly added identity " "attributes(if any)\n"))


def local_chain_is_updated(miner_address, length_of_local_chain):
    print("Using the Gossip protocol of FoBSim, the local chain of the following miner was updated:")
    print(f"Miner: {str(miner_address)}")
    print(f"The length of the new local chain: {str(length_of_local_chain)}")


def mempool_is_empty():
    print("mempool is empty")


def finish():
    print("simulation is done.")
    print("To check/analyze the experiment, please refer to the temporary folder.")
    print("There, you can find:")
    print("- miners' local chains")
    print("- miners' local records of users' wallets")
    print("- log of blocks confirmed by the majority of miners")
    print("- log of final amounts in miners' wallets (initial values - staked values + awards)")
    print("- log of values which were staked by miners")
    print("thank YOU..!")
