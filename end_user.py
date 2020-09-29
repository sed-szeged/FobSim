import random
from random import randrange
import json
import output

with open("Sim_parameters.json") as json_file:
    data = json.load(json_file)


class User:
    def __init__(self, address, parent):
        self.addressParent = parent
        self.addressSelf = address
        self.tasks = []
        self.identity_added_attributes = {}
        self.wallet = data["EUs_initial_wallet_value"]

    def create_tasks(self, num_of_task_per_user, blockchain_function, list_of_end_users):
        if blockchain_function == 1:
            for l in range(num_of_task_per_user):
                self.tasks.append(random.randint(0, 1000000))
            output.txs_success(num_of_task_per_user, self.addressParent, self.addressSelf)

        if blockchain_function == 2:
            operations = ['+', '-', '*', '/']
            for i in range(num_of_task_per_user):
                operation = random.choice(operations)
                random_computational_task = str(randrange(1000)) + operation + str(randrange(1000))
                self.tasks.append([self.addressParent, self.addressSelf, random_computational_task])
        if blockchain_function == 3:
            for i in range(num_of_task_per_user):
                payment = randrange(round(self.wallet/len(list_of_end_users), 0))
                receiver = random.choice(list_of_end_users)
                receiver_parent_address = receiver.addressParent
                receiver_individual_address = receiver.addressSelf
                proposed_transaction = [payment, self.addressParent, self.addressSelf, receiver_parent_address, receiver_individual_address]
                self.tasks.append(proposed_transaction)
        if blockchain_function == 4:
            add_new_attributes(self)
            proposed_transaction = [self.addressParent, self.addressSelf, self.identity_added_attributes]
            self.tasks.append(proposed_transaction)

    def send_tasks(self, list_of_fog_nodes):
        for obj in list_of_fog_nodes:
            if obj.address == self.addressParent:
                obj.receive_tasks(self.tasks, self.addressSelf)


def add_new_attributes(user):
    for key in user.identity_added_attributes:
        user.identity_added_attributes[key] = input(
            str(user.addressParent) + "." + str(user.addressSelf) + ": " + key + ">> ")
