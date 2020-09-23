import blockchain
import consensus
import json
import os

with open("Sim_parameters.json") as json_file:
    data = json.load(json_file)


class Miner:
    def __init__(self, address):
        self.address = "Miner_" + str(address)
        self.isAuthorized = False
        self.next_pos_block_from = self

    def build_block(self, num_of_tx_per_block, mempool, miner_list, type_of_consensus, list_of_end_users, blockchain_function):
        if type_of_consensus == 3 and not self.isAuthorized:
            print("Miner: " + self.address + " is not authorized to generate a new block..!")
        else:
            if blockchain_function == 3:
                transactions = self.validate_transmitted_transactions(accumulate_transactions(num_of_tx_per_block, mempool, blockchain_function, self.address))
            else:
                transactions = accumulate_transactions(num_of_tx_per_block, mempool, blockchain_function, self.address)
            if type_of_consensus == 1:
                new_block = consensus.pow_mining(blockchain.generate_new_block(transactions, self.address))
            if type_of_consensus == 2 or (type_of_consensus == 3 and self.isAuthorized):
                new_block = blockchain.generate_new_block(transactions, self.address)
            with open(str("temporary/" + self.address + "_local_chain.json"), 'r') as f:
                temporary_local_chain = json.load(f)
                new_block['previous_hash'] = temporary_local_chain[str(len(temporary_local_chain) - 1)]['hash']
            self.print_the_block_broadcast_info(new_block)
            print("*****************\nThe new block is broadcast and miner nodes will "
                  "add it to their local chains (if valid)\n")
            for elem in miner_list:
                elem.receive_new_block(mempool, new_block, type_of_consensus, miner_list, blockchain_function,
                                       list_of_end_users)

    def validate_transmitted_transactions(self, list_of_new_transactions):
        with open(str("temporary/" + self.address + "_users_wallets.json"), "r") as user_wallets_external_file:
            user_wallets_temporary_file = json.load(user_wallets_external_file)
            for i in range(len(list_of_new_transactions)):
                for key in user_wallets_temporary_file:
                    if key == (str(list_of_new_transactions[i][1]) + "." + str(list_of_new_transactions[i][2])):
                        if user_wallets_temporary_file[key]['wallet_value'] < list_of_new_transactions[i][0]:
                            print("the following transaction is illegal:")
                            print(list_of_new_transactions[i])
                            print("the end_user_wallet contains only " + str(user_wallets_temporary_file[key]['wallet_value']) + " digital coins..!")
                            print("the transaction is withdrawn from the block")
                            del list_of_new_transactions[i]
        return list_of_new_transactions

    def print_the_block_broadcast_info(self, new_block):
        print("The following block has been proposed by " + self.address +
              " and is generated into the Blockchain network")
        print("**************************")
        print("transactions:")
        print(new_block['transactions'])
        print("hash:")
        print(new_block['hash'])
        print("timestamp:")
        print(new_block['timestamp'])
        print("nonce:")
        print(new_block['nonce'])
        print("previous_hash:")
        print(new_block['previous_hash'])
        print("**************************")

    def receive_new_block(self, mempool, new_block, type_of_consensus, miner_list, blockchain_function, list_of_end_users):
        with open(str("temporary/" + self.address + "_local_chain.json"), 'r') as f:
            local_chain_temporary_file = json.load(f)
        print("a new block is received from " + str(new_block['generator_id']))
        if (len(local_chain_temporary_file) == 0 and new_block['generator_id'] == 'The Network') \
                or (type_of_consensus == 1 and consensus.pow_block_is_valid(new_block, local_chain_temporary_file[str(len(local_chain_temporary_file) - 1)]['hash'], list_of_end_users, blockchain_function))\
                or (type_of_consensus == 2 and new_block['generator_id'] == self.next_pos_block_from) \
                or (type_of_consensus == 3 and consensus.poa_block_is_valid(new_block, local_chain_temporary_file[str(len(local_chain_temporary_file) - 1)]['hash'], miner_list, blockchain_function, list_of_end_users)):
            self.add(new_block, miner_list, blockchain_function)
        else:
            print("The proposed block is not valid."
                  "\nTransactions will be sent back to the mempool and mined again..!")
            blockchain.txs_back_to_memp(new_block['transactions'], mempool)

    def validate_received_transactions(self, list_of_new_transactions):
        with open(str("temporary/" + self.address + "_users_wallets.json"), 'r') as f:
            user_wallets_temporary_file = json.load(f)
        for i in range(len(list_of_new_transactions)):
            for key in user_wallets_temporary_file:
                if key == (str(list_of_new_transactions[i][1]) + "." + str(list_of_new_transactions[i][2])):
                    if user_wallets_temporary_file[key]['wallet_value'] >= list_of_new_transactions[i][0]:
                        user_wallets_temporary_file[key]['wallet_value'] -= list_of_new_transactions[i][0]
                    else:
                        return False
                if key == (str(list_of_new_transactions[i][3]) + "." + str(list_of_new_transactions[i][4])):
                    user_wallets_temporary_file[key]['wallet_value'] += list_of_new_transactions[i][0]
        os.remove(str("temporary/" + self.address + "_users_wallets.json"))
        with open(str("temporary/" + self.address + "_users_wallets.json"), "w") as f:
            json.dump(user_wallets_temporary_file, f, indent=4)
        return True

    def add(self, block, list_of_miners, blockchain_function):
        ready = False
        local_chain_external_file = open(str("temporary/" + self.address + "_local_chain.json"))
        local_chain_temporary_file = json.load(local_chain_external_file)
        local_chain_external_file.close()
        if len(local_chain_temporary_file) == 0:
            top_block = block
            top_block['next'] = None
            block['previous_hash'] = 0
            ready = True
        else:
            if blockchain_function != 3 or (
                    blockchain_function == 3 and self.validate_received_transactions(block['transactions'])):
                top_block = local_chain_temporary_file[str(len(local_chain_temporary_file) - 1)]
                top_block['next'] = block['hash']
                block['previous_hash'] = top_block['hash']
                blockchain.report_a_successful_block_addition(block['generator_id'], block['hash'])
                print("*******************************************")
                print("the block is now added to the local chain of " + self.address)
                if block['generator_id'] != self.address:
                    print("this block was received from " + block['generator_id'])
                block['blockNo'] = len(local_chain_temporary_file)
                ready = True
        if ready:
            local_chain_temporary_file[str(len(local_chain_temporary_file))] = block
            os.remove(str("temporary/" + self.address + "_local_chain.json"))
            with open(str("temporary/" + self.address + "_local_chain.json"), "w") as f:
                json.dump(local_chain_temporary_file, f, indent=4)
            print("##############################\n")


def accumulate_transactions(num_of_tx_per_block, mempool, blockchain_function, miner_address):
    lst_of_transactions = []
    if mempool.qsize() > 0:
        if blockchain_function == 2:
            transaction = mempool.get()
            transaction.append(eval(transaction[2]))
            produced_transaction = ['End-user address: ' + str(transaction[0]) + '.' + str(transaction[1]), 'Requested computational task: ' + str(transaction[2]),
                                    'Result: ' + str(transaction[3]), "miner: " + str(miner_address)]
            return produced_transaction
        else:
            for i in range(num_of_tx_per_block):
                lst_of_transactions.append(mempool.get())
            return lst_of_transactions
