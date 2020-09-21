import time
import hashlib
import json
import memPool
from multiprocessing import Manager

with open("Sim_parameters.json") as json_file:
    data = json.load(json_file)
diff = data["puzzle_difficulty"]
target = 2 ** (256 - diff)
list_of_stakes = [['Network', 0]]


class Block:

    def __init__(self, tx, generator_id):
        self.transactions = tx
        self.next = None
        self.blockNo = 0
        self.nonce = 0
        self.generator_id = generator_id
        self.previous_hash = 0
        self.timestamp = time.time()
        self.hash = hashing_function(self.nonce, self.transactions, self.generator_id)


class AwardLog:
    def __init__(self):
        self.mining_award = 5
        self.awards_log = []

    def report_a_successful_block_addition(self, winning_miner, hash_of_added_block, list_of_miners):
        record_exist = False
        for award_log in self.awards_log:
            if award_log[0] == winning_miner and award_log[1] == hash_of_added_block:
                award_log[2] += 1
                record_exist = True
                break
        if not record_exist:
            self.awards_log.append([winning_miner, hash_of_added_block, 1])

    def declare_winning_miners(self, number_of_miners):
        while len(self.awards_log) != 0:
            if self.awards_log[0][2] >= int(number_of_miners / 2):
                memPool.winning_miners.put(self.awards_log[0][0])
                self.awards_log.remove(self.awards_log[0])

    def award_winning_miners(self, list_of_miners):
        while memPool.winning_miners.qsize() != 0:
            winner = memPool.winning_miners.get()
            for miner in list_of_miners:
                if miner.address == winner:
                    miner.wallet += 5
                    break

def txs_back_to_memp(returned_transactions, mem_pool):
    for i in range(len(returned_transactions)):
        mem_pool.put(returned_transactions[i])


def hashing_function(nonce, transactions, generator_id):
    h = hashlib.sha256()
    h.update(str(nonce).encode(encoding='UTF-8') + str(transactions).encode(encoding='UTF-8')
             + str(generator_id).encode(encoding='UTF-8'))
    return h.hexdigest()


def stake(miner_address, amount, list_of_miners):
    if miner_address in [elem for sublist in list_of_stakes for elem in sublist]:
        for stake_record in list_of_stakes:
            if stake_record[0] == miner_address:
                stake_record[1] += amount
                break
    else:
        list_of_stakes.append([miner_address, amount])
    for miner in list_of_miners:
        if miner.address == miner_address:
            miner.wallet -= amount
            print(str(miner.address) + " have staked " + str(amount) + " successfully.")
            print(str(miner.address) + " wallet contains now " + str(miner.wallet))
            break


def read_the_stake(miner_address):
    if miner_address in [elem for sublist in list_of_stakes for elem in sublist]:
        for stake_record in list_of_stakes:
            if stake_record[0] == miner_address:
                return stake_record[1]
    else:
        return 0
