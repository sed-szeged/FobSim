# import blockchain
# import json
# import output
# import modification
#
# num_of_consensus = 0
# blockchain_CAs = ['1', '2', '3']
#
#
# def choose_consensus():
#     while True:
#         output.choose_consensus()
#         global num_of_consensus
#         num_of_consensus = input()
#         if num_of_consensus in blockchain_CAs:
#             num_of_consensus = int(num_of_consensus)
#             if num_of_consensus == 2:
#                 modification.write_file('temporary/miners_stake_amounts.json', {})
#             break
#         else:
#             print("Input is incorrect, try again..!")
#     return num_of_consensus
#
#
# def pow_mining(block):
#     while True:
#         block['hash'] = blockchain.hashing_function(block['nonce'], block['transactions'], block['generator_id'], block['previous_hash'])
#         if int(block['hash'], 16) > blockchain.target:
#             block['nonce'] += 1
#         else:
#             break
#     return block
#
#
# def pow_block_is_valid(block, expected_previous_hash):
#     block_is_valid = False
#     condition_1 = block['hash'] == blockchain.hashing_function(block['nonce'], block['transactions'], block['generator_id'], expected_previous_hash)
#     condition_2 = int(block['hash'], 16) <= blockchain.target
#     if condition_1 and condition_2:
#         block_is_valid = True
#     return block_is_valid
#
#
# def poa_block_is_valid(block, expected_previous_hash, miner_list):
#     for obj in miner_list:
#         if obj.address == block['generator_id'] \
#                 and obj.isAuthorized \
#                 and block['previous_hash'] == expected_previous_hash \
#                 and block['hash'] == blockchain.hashing_function(block['nonce'], block['transactions'], block['generator_id'], block['previous_hash']):
#             return True
#     return False
