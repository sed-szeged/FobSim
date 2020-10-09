import blockchain
import consensus
import json
import os
import time
import output
import hashlib


class Miner:
    def __init__(self, address):
        self.address = "Miner_" + str(address)
        self.top_block = {}
        self.isAuthorized = False
        self.next_pos_block_from = self.address
        self.neighbours = set()

    def build_block(self, num_of_tx_per_block, mempool, miner_list, type_of_consensus, blockchain_function, discarded_txs):
        self.gossip(blockchain_function)
        if type_of_consensus == 3 and not self.isAuthorized:
            output.unauthorized_miner_msg(self.address)
        else:
            accumulated_transactions = accumulate_transactions(num_of_tx_per_block, mempool, blockchain_function, self.address)
            if accumulated_transactions:
                transactions = accumulated_transactions
                if blockchain_function == 3:
                    transactions = self.validate_transactions(transactions, "generator")
                if type_of_consensus == 1:
                    new_block = consensus.pow_mining(blockchain.generate_new_block(transactions, self.address, self.top_block['hash']))
                if type_of_consensus == 2 or (type_of_consensus == 3 and self.isAuthorized):
                    new_block = blockchain.generate_new_block(transactions, self.address, self.top_block['hash'])
                output.block_info(new_block, type_of_consensus)
                for elem in miner_list:
                    if elem.address in self.neighbours:
                        elem.receive_new_block(new_block, type_of_consensus, miner_list, blockchain_function, discarded_txs)

    def receive_new_block(self, new_block, type_of_consensus, miner_list, blockchain_function, discarded_txs):
        while True:
            try:
                with open(str("temporary/" + self.address + "_local_chain.json"), 'r') as f:
                    local_chain_temporary_file = json.load(f)
                    break
            except:
                time.sleep(0.3)
        print("a new block is received from " + str(new_block['generator_id']))
        condition_1 = (len(local_chain_temporary_file) == 0) and (new_block['generator_id'] == 'The Network')
        if condition_1:
            self.add(new_block, blockchain_function)
        else:
            list_of_hashes_in_local_chain = []
            for key in local_chain_temporary_file:
                list_of_hashes_in_local_chain.append(local_chain_temporary_file[key]['hash'])
            if new_block['hash'] not in list_of_hashes_in_local_chain:
                condition_2 = type_of_consensus == 1 and consensus.pow_block_is_valid(new_block, self.top_block['hash'])
                condition_3 = type_of_consensus == 2 and new_block['generator_id'] == self.next_pos_block_from
                condition_4 = type_of_consensus == 3 and consensus.poa_block_is_valid(new_block, self.top_block['hash'], miner_list)
                if condition_2 or condition_3 or condition_4:
                    self.add(new_block, blockchain_function)
                    for elem in miner_list:
                        if elem.address in self.neighbours:
                            elem.receive_new_block(new_block, type_of_consensus, miner_list, blockchain_function,
                                                   discarded_txs)
                else:
                    output.illegal_block()
                    if new_block['transactions']:
                        for tx in new_block['transactions']:
                            discarded_txs.put(tx)
            else:
                output.block_discarded()

    def validate_transactions(self, list_of_new_transactions, miner_role):
        while True:
            try:
                with open(str("temporary/" + self.address + "_users_wallets.json"), "r") as user_wallets_external_file:
                    user_wallets_temporary_file = json.load(user_wallets_external_file)
                    break
            except:
                time.sleep(0.1)
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
            while True:
                try:
                    os.remove(str("temporary/" + self.address + "_users_wallets.json"))
                    with open(str("temporary/" + self.address + "_users_wallets.json"), "w") as f:
                        json.dump(user_wallets_temporary_file, f, indent=4)
                        break
                except:
                    time.sleep(0.1)
            return True
        if miner_role == "generator":
            return list_of_new_transactions

    def add(self, block, blockchain_function):
        ready = False
        while True:
            try:
                local_chain_external_file = open(str("temporary/" + self.address + "_local_chain.json"))
                local_chain_temporary_file = json.load(local_chain_external_file)
                local_chain_external_file.close()
                break
            except:
                time.sleep(0.2)
        if len(local_chain_temporary_file) == 0:
            ready = True
        else:
            if blockchain_function != 3 or (
                    blockchain_function == 3 and self.validate_transactions(block['transactions'], "receiver")):
                if block['previous_hash'] == self.top_block['hash']:
                    blockchain.report_a_successful_block_addition(block['generator_id'], block['hash'])
                    output.block_success_addition(self.address, block['generator_id'])
                    ready = True
        if ready:
            block['blockNo'] = len(local_chain_temporary_file)
            block['timestamp'] = time.ctime()
            self.top_block = block
            local_chain_temporary_file[str(len(local_chain_temporary_file))] = block
            while True:
                try:
                    os.remove(str("temporary/" + self.address + "_local_chain.json"))
                    with open(str("temporary/" + self.address + "_local_chain.json"), "w") as f:
                        json.dump(local_chain_temporary_file, f, indent=4)
                        break
                except:
                    time.sleep(0.1)

    def gossip(self, blockchain_function):
        while True:
            try:
                with open(str("temporary/" + self.address + "_local_chain.json"), "r") as f:
                    local_chain_temporary_file = json.load(f)
                    break
            except:
                time.sleep(0.01)
        confirmed_chain = local_chain_temporary_file
        max_votes_for_confirmed_chain = 1
        votes_for_confirmed_chain = {str(hashing(local_chain_temporary_file)): [local_chain_temporary_file, 1, self.address]}
        confirmed_chain_from = self.address
        local_chain_is_updated = False
        for neighbour in self.neighbours:
            key_exist = False
            while True:
                try:
                    with open(str("temporary/" + neighbour + "_local_chain.json"), "r") as f:
                        local_chain_temp_file = json.load(f)
                        break
                except:
                    time.sleep(0.1)
            for key in votes_for_confirmed_chain:
                if key == str(hashing(local_chain_temp_file)):
                    votes_for_confirmed_chain[key][1] += 1
                    key_exist = True
                    break
            if not key_exist:
                votes_for_confirmed_chain[str(hashing(local_chain_temp_file))] = [local_chain_temp_file, 1, neighbour]
        for key in votes_for_confirmed_chain:
            temp_list = votes_for_confirmed_chain[key]
            if temp_list[1] > max_votes_for_confirmed_chain:
                local_chain_is_updated = True
                confirmed_chain = temp_list[0]
                max_votes_for_confirmed_chain = temp_list[1]
                confirmed_chain_from = temp_list[2]
        if local_chain_is_updated:
            while True:
                try:
                    os.remove(str("temporary/" + self.address + "_local_chain.json"))
                    with open(str("temporary/" + self.address + "_local_chain.json"), "w") as m:
                        json.dump(confirmed_chain, m, indent=4)
                        if blockchain_function == 3:
                            with open(str("temporary/" + confirmed_chain_from + "_users_wallets.json"), "r") as t:
                                user_wallets_temp_file = json.load(t)
                            os.remove(str("temporary/" + self.address + "_users_wallets.json"))
                            with open(str("temporary/" + self.address + "_users_wallets.json"), "w") as n:
                                json.dump(user_wallets_temp_file, n, indent=4)
                    break
                except:
                    time.sleep(0.1)
            self.top_block = confirmed_chain[str(len(confirmed_chain)-1)]
            output.local_chain_is_updated(self.address, max_votes_for_confirmed_chain, len(confirmed_chain))


def hashing(dictionary):
    h = hashlib.sha256()
    h.update(str(dictionary).encode(encoding='UTF-8'))
    return h.hexdigest()


def accumulate_transactions(num_of_tx_per_block, mempool, blockchain_function, miner_address):
    lst_of_transactions = []
    if blockchain_function == 2:
        if mempool.qsize() > 0:
            transaction = mempool.get()
            transaction.append(eval(transaction[2]))
            produced_transaction = ['End-user address: ' + str(transaction[0]) + '.' + str(transaction[1]),
                                    'Requested computational task: ' + str(transaction[2]), 'Result: '
                                    + str(transaction[3]), "miner: " + str(miner_address)]
            return produced_transaction
        else:
            output.mempool_is_empty()
    else:
        for i in range(num_of_tx_per_block):
            if mempool.qsize() > 0:
                lst_of_transactions.append(mempool.get())
            else:
                output.mempool_is_empty()
                break
        return lst_of_transactions
