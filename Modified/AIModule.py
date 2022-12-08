import random

import blockchain
import encryption_module

ML_model = None


def predict_nonce(block):
    return random.randrange(10, 4000000000)
    # return ML_model.predict(int(blockchain.get_max_hash(), 16),
    #                         int(encryption_module.hashing_function(block['Body']['transactions']), 16),
    #                         True,
    #                         blockchain.diff)
