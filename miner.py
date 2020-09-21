import blockchain
import consensus
from multiprocessing import Manager
import json

with open("Sim_parameters.json") as json_file:
    data = json.load(json_file)


class Miner:
    def __init__(self, address):
        self.address = "Miner_" + str(address)
        manger = Manager()
        self.local_chain = manger.list()
        self.users_wallets = []
        self.isAuthorized = False
        self.wallet = data["miners_initial_wallet_value"]
        self.next_pos_block_from = self

    def build_block(self, num_of_tx_per_block, mempool, miner_list, type_of_consensus, list_of_end_users, blockchain_function, award_log):
        if type_of_consensus == 3 and not self.isAuthorized:
            print("Miner: " + self.address + " is not authorized to generate a new block..!")
        else:
            if blockchain_function == 3:
                transactions = self.validate_transmitted_transactions(accumulate_transactions(num_of_tx_per_block, mempool, blockchain_function, self.address))
            else:
                transactions = accumulate_transactions(num_of_tx_per_block, mempool, blockchain_function, self.address)
            if type_of_consensus == 1:
                new_block = consensus.pow_mining(blockchain.Block(transactions, self.address))
            if type_of_consensus == 2 or (type_of_consensus == 3 and self.isAuthorized):
                new_block = blockchain.Block(transactions, self.address)
            new_block.previous_hash = self.local_chain[-1].hash
            self.print_the_block_broadcast_info(new_block)
            for elem in miner_list:
                elem.receive_new_block(mempool, new_block, type_of_consensus, miner_list, blockchain_function,
                                       list_of_end_users, award_log)
            print("*****************\nThe new block is broadcast and miner nodes will "
                  "add it to their local chains (if valid)\n")

    def validate_transmitted_transactions(self, list_of_new_transactions):
        for i in range(len(list_of_new_transactions)):
            for wallet in self.users_wallets:
                if list_of_new_transactions[i][1] == wallet[0] and list_of_new_transactions[i][2] == wallet[1]:
                    if wallet[2] < list_of_new_transactions[i][0]:
                        print("the following transaction is illegal:")
                        print(list_of_new_transactions[i])
                        print("the end_user_wallet contains only " + str(wallet[2]) + " digital coins..!")
                        print("the transaction is withdrawn from the block")
                        del list_of_new_transactions[i]
        return list_of_new_transactions

    def print_the_block_broadcast_info(self, new_block):
        print("The following block has been proposed by " + self.address +
              " and is generated into the Blockchain network")
        print("**************************")
        print("transactions:")
        print(new_block.transactions)
        print("hash:")
        print(new_block.hash)
        print("timestamp:")
        print(new_block.timestamp)
        print("nonce:")
        print(new_block.nonce)
        print("previous_hash:")
        print(new_block.previous_hash)
        print("**************************")

    def receive_new_block(self, mempool, new_block, type_of_consensus, miner_list, blockchain_function, list_of_end_users, award_log):
        print("a new block is received from " + new_block.generator_id)
        if len(self.local_chain) == 0 and new_block.generator_id == 'The Network':
            self.add(new_block, miner_list, award_log, blockchain_function)
            print("genesis block is received")
        else:
            if (type_of_consensus == 1 and consensus.pow_block_is_valid(new_block, self.local_chain[-1].hash, list_of_end_users)) \
                    or (type_of_consensus == 2 and new_block.generator_id == self.next_pos_block_from) \
                    or (type_of_consensus == 3 and consensus.poa_block_is_valid(new_block, self.local_chain[-1].hash, miner_list, blockchain_function, list_of_end_users)):
                self.add(new_block, miner_list, award_log, blockchain_function)
            else:
                print("The proposed block is not valid."
                      "\nTransactions will be sent back to the mempool and mined again..!")
                blockchain.txs_back_to_memp(new_block.transactions, mempool)

    def validate_received_transactions(self, list_of_new_transactions):
        for i in range(len(list_of_new_transactions)):
            for wallet in self.users_wallets:
                if list_of_new_transactions[i][1] == wallet[0] and list_of_new_transactions[i][2] == wallet[1]:
                    if wallet[2] >= list_of_new_transactions[i][0]:
                        wallet[2] -= list_of_new_transactions[i][0]
                    else:
                        return False
                if list_of_new_transactions[i][3] == wallet[0] and list_of_new_transactions[i][4] == wallet[1]:
                    wallet[2] += list_of_new_transactions[i][0]
        return True

    def print_miner_local_chain(self):
        print(self.address)
        # print("This miner reputation is " + str(self.reputation))
        for obj in self.local_chain:
            print(obj.transactions)
        print("*******************************************")

    def add(self, block, list_of_miners, award_log, blockchain_function):
        if len(self.local_chain) == 0:
            top_block = block
            top_block.next = None
            block.previous_hash = 0
        else:
            if blockchain_function != 3 or (
                    blockchain_function == 3 and self.validate_received_transactions(block.transactions)):
                top_block = self.local_chain[-1]
                top_block.next = block
                block.previous_hash = top_block.hash
                award_log.report_a_successful_block_addition(block.generator_id, block.hash, list_of_miners)
                print("*******************************************")
                print("the block was added to the local chain of " + self.address)
                if block.generator_id != self.address:
                    print("this block was received from " + block.generator_id)
                print("Local chain is now as following:")
                for obj in self.local_chain:
                    print(str(obj.blockNo) + ": number of transactions: " + str(
                        len(obj.transactions)) + "\ngenerator id: " + obj.generator_id)
                print("*******************************************")
                if blockchain_function == 3:
                    print("Local record of user wallets is now as following:")
                    for wallet in self.users_wallets:
                        print(str(wallet[0]) + "." + str(
                            wallet[1]) + ": " + str(wallet[2]))
                    print("*******************************************")
        block.blockNo = len(self.local_chain)
        self.local_chain.append(block)


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
