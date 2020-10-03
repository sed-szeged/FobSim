import blockchain
import consensus
import json
import os
import time
import output

with open("Sim_parameters.json") as json_file:
    data = json.load(json_file)


class Miner:
    def __init__(self, address):
        self.address = "Miner_" + str(address)
        self.top_block = {}
        self.isAuthorized = False
        self.next_pos_block_from = self.address

    def build_block(self, num_of_tx_per_block, mempool, miner_list, type_of_consensus, blockchain_function):
        if type_of_consensus == 3 and not self.isAuthorized:
            print("Miner: " + self.address + " is not authorized to generate a new block..!")
        else:
            if blockchain_function == 3:
                transactions = self.validate_transactions(accumulate_transactions(num_of_tx_per_block, mempool, blockchain_function, self.address), "generator")
            else:
                transactions = accumulate_transactions(num_of_tx_per_block, mempool, blockchain_function, self.address)
            if type_of_consensus == 1:
                new_block = consensus.pow_mining(blockchain.generate_new_block(transactions, self.address, self.top_block['hash']))
            if type_of_consensus == 2 or (type_of_consensus == 3 and self.isAuthorized):
                new_block = blockchain.generate_new_block(transactions, self.address, self.top_block['hash'])
            output.block_info(new_block, type_of_consensus)
            for elem in miner_list:
                elem.receive_new_block(mempool, new_block, type_of_consensus, miner_list, blockchain_function)

    def receive_new_block(self, mempool, new_block, type_of_consensus, miner_list, blockchain_function):
        with open(str("temporary/" + self.address + "_local_chain.json"), 'r') as f:
            local_chain_temporary_file = json.load(f)
        print("a new block is received from " + str(new_block['generator_id']))
        condition_1 = (len(local_chain_temporary_file) == 0) and (new_block['generator_id'] == 'The Network')
        if condition_1:
            self.add(new_block, blockchain_function)
        else:
            condition_2 = type_of_consensus == 1 and consensus.pow_block_is_valid(new_block, self.top_block['hash'])
            condition_3 = type_of_consensus == 2 and new_block['generator_id'] == self.next_pos_block_from
            condition_4 = type_of_consensus == 3 and consensus.poa_block_is_valid(new_block, self.top_block['hash'], miner_list)
            if condition_2 or condition_3 or condition_4:
                self.add(new_block, blockchain_function)
            else:
                output.illegal_block()
                blockchain.txs_back_to_memp(new_block['transactions'], mempool)

    def validate_transactions(self, list_of_new_transactions, miner_role):
        with open(str("temporary/" + self.address + "_users_wallets.json"), "r") as user_wallets_external_file:
            user_wallets_temporary_file = json.load(user_wallets_external_file)
        if list_of_new_transactions:
            for tx in list_of_new_transactions:
                for key in user_wallets_temporary_file:
                    if miner_role == "receiver":
                        if key == (str(tx[1]) + "." + str(tx[2])):
                            if user_wallets_temporary_file[key]['wallet_value'] >= tx[0]:
                                user_wallets_temporary_file[key]['wallet_value'] -= tx[0]
                            else:
                                return False
                        if key == (str(tx[3]) + "." + str(tx[4])):
                            user_wallets_temporary_file[key]['wallet_value'] += tx[0]
                    if miner_role == "generator":
                        if user_wallets_temporary_file[key]['wallet_value'] < tx[0]:
                            output.illegal_tx(tx, user_wallets_temporary_file[key]['wallet_value'])
                            del tx
        if miner_role == "receiver":
            os.remove(str("temporary/" + self.address + "_users_wallets.json"))
            with open(str("temporary/" + self.address + "_users_wallets.json"), "w") as f:
                json.dump(user_wallets_temporary_file, f, indent=4)
            return True
        if miner_role == "generator":
            return list_of_new_transactions

    def add(self, block, blockchain_function):
        ready = False
        local_chain_external_file = open(str("temporary/" + self.address + "_local_chain.json"))
        local_chain_temporary_file = json.load(local_chain_external_file)
        local_chain_external_file.close()
        if len(local_chain_temporary_file) == 0:
            self.top_block = block
            ready = True
        else:
            if blockchain_function != 3 or (
                    blockchain_function == 3 and self.validate_transactions(block['transactions'], "receiver")):
                if block['previous_hash'] == self.top_block['hash']:
                    self.top_block = block
                    blockchain.report_a_successful_block_addition(block['generator_id'], block['hash'])
                    output.block_success_addition(self.address, block['generator_id'])
                    ready = True
        if ready:
            block['blockNo'] = len(local_chain_temporary_file)
            block['timestamp'] = time.ctime()
            local_chain_temporary_file[str(len(local_chain_temporary_file))] = block
            os.remove(str("temporary/" + self.address + "_local_chain.json"))
            with open(str("temporary/" + self.address + "_local_chain.json"), "w") as f:
                json.dump(local_chain_temporary_file, f, indent=4)


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
