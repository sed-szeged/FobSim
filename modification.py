import random
import json
import os
import time
import shutil


def initiate_files(gossip_activated):
    for filename in os.listdir('temporary'):
        file_path = os.path.join('temporary', filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))
    write_file('temporary/confirmation_log.json', {})
    write_file('temporary/miner_wallets_log.json', {})
    if gossip_activated:
        write_file('temporary/longest_chain.json', {'chain': {}, 'from': 'Miner_1'})


def read_file(file_path):
    random_waiting_time = random.randint(1, 10) / 100
    while True:
        try:
            with open(file_path, 'r') as f:
                file = json.load(f)
                break
        except Exception as e:
            # print(e)
            time.sleep(random_waiting_time)
    return file


def write_file(file_path, contents):
    with open(file_path, 'w') as f:
        json.dump(contents, f, indent=4)


def rewrite_file(file_path, new_version):
    random_waiting_time = random.randint(1, 10)/100
    while True:
        try:
            os.remove(file_path)
            with open(file_path, "w") as f:
                json.dump(new_version, f, indent=4)
            break
        except Exception as e:
            # print(e)
            time.sleep(random_waiting_time)
