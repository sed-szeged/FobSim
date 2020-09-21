import blockchain
import main
import random

num_of_consensus = 0


def choose_consensus():
    print("Please choose the Consensus algorithm to be used in the simulation:\n"
          "(1) Proof of Work: PoW\n"
          "(2) Proof of Stake: PoS\n"
          "(3) Proof of Authority: PoA\n")
    global num_of_consensus
    num_of_consensus = int(input())
    return num_of_consensus


def pow_mining(block):
    for i in range(500000000):
        block.hash = blockchain.hashing_function(block.nonce, block.transactions, block.generator_id)
        if int(block.hash, 16) > blockchain.target:
            block.nonce += 1
        else:
            break
    return block


def pow_block_is_valid(block, expected_previous_hash, list_of_end_users):
    if block.hash == blockchain.hashing_function(block.nonce, block.transactions, block.generator_id):
        if int(block.hash, 16) <= blockchain.target and block.previous_hash == expected_previous_hash:
            if main.blockchainFunction == 3:
                if not payments_are_legal(block.transactions, list_of_end_users):
                    return True
                else:
                    return False
            return True


def payments_are_legal(transactions, list_of_end_users):
    for i in range(len(transactions)):
        for user in list_of_end_users:
            if user.addressParent == transactions[i][1] and user.addressSelf == transactions[i][2]:
                if user.wallet < transactions[i][0]:
                    return False
                else:
                    return True


def poa_block_is_valid(block, expected_previous_hash, miner_list, blockchain_function, list_of_end_users):
    for obj in miner_list:
        if obj.address == block.generator_id:
            if obj.isAuthorized and block.previous_hash == expected_previous_hash:
                if block.hash == blockchain.hashing_function(block.nonce, block.transactions, block.generator_id):
                    if blockchain_function == 3:
                        if payments_are_legal(block.transactions, list_of_end_users):
                            return True
                        else:
                            return False
                    return True


def pos_miners_staking(list_of_miners):
    if num_of_consensus == 2:
        for miner in list_of_miners:
            blockchain.stake(miner.address, random.randint(0, miner.wallet), list_of_miners)
