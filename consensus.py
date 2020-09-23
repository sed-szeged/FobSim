import blockchain
import json

num_of_consensus = 0


def choose_consensus():
    print("Please choose the Consensus algorithm to be used in the simulation:\n"
          "(1) Proof of Work: PoW\n"
          "(2) Proof of Stake: PoS\n"
          "(3) Proof of Authority: PoA\n")
    global num_of_consensus
    num_of_consensus = int(input())
    if num_of_consensus == 2:
        with open('temporary/miners_stake_amounts.json', 'w') as file:
            json.dump({}, file, indent=4)
    return num_of_consensus


def pow_mining(block):
    while True:
        block['hash'] = blockchain.hashing_function(block['nonce'], block['transactions'], block['generator_id'])
        if int(block['hash'], 16) > blockchain.target:
            block['nonce'] += 1
        else:
            break
    return block


def pow_block_is_valid(block, expected_previous_hash, list_of_end_users, blockchainFunction):
    if block['hash'] == blockchain.hashing_function(block['nonce'], block['transactions'], block['generator_id']):
        if int(block['hash'], 16) <= blockchain.target and block['previous_hash'] == expected_previous_hash:
            return True


def poa_block_is_valid(block, expected_previous_hash, miner_list, blockchain_function, list_of_end_users):
    for obj in miner_list:
        if obj.address == block['generator_id']:
            if obj.isAuthorized and block['previous_hash'] == expected_previous_hash:
                if block['hash'] == blockchain.hashing_function(block['nonce'], block['transactions'], block['generator_id']):
                    return True



