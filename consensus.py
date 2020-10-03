import blockchain
import json
import output
num_of_consensus = 0
blockchain_CAs = [1, 2, 3]


def choose_consensus():
    while True:
        output.choose_consensus()
        global num_of_consensus
        num_of_consensus = int(input())
        if check_input(num_of_consensus, blockchain_CAs):
            if num_of_consensus == 2:
                with open('temporary/miners_stake_amounts.json', 'w') as file:
                    json.dump({}, file, indent=4)
            break
        else:
            print("Input is incorrect, try again..!")
    return num_of_consensus


def check_input(input_value, reference_list):
    while True:
        if input_value in reference_list:
            return True
        else:
            return False


def pow_mining(block):
    while True:
        block['hash'] = blockchain.hashing_function(block['nonce'], block['transactions'], block['generator_id'], block['previous_hash'])
        if int(block['hash'], 16) > blockchain.target:
            block['nonce'] += 1
        else:
            break
    return block


def pow_block_is_valid(block, expected_previous_hash):
    if block['hash'] == blockchain.hashing_function(block['nonce'], block['transactions'], block['generator_id'], expected_previous_hash):
        if int(block['hash'], 16) <= blockchain.target:
            return True


def poa_block_is_valid(block, expected_previous_hash, miner_list):
    for obj in miner_list:
        if obj.address == block['generator_id']:
            if obj.isAuthorized and block['previous_hash'] == expected_previous_hash:
                if block['hash'] == blockchain.hashing_function(block['nonce'], block['transactions'], block['generator_id'], block['previous_hash']):
                    return True
