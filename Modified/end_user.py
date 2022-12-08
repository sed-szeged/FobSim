import random
from random import randrange
import output
import modification

data = modification.read_file("Sim_parameters.json")


class User:
    def __init__(self, address, parent):
        self.addressParent = parent
        self.addressSelf = address
        self.tasks = []
        self.identity_added_attributes = {}
        self.wallet = data["Max_enduser_payment"] * data["NumOfTaskPerUser"]
        self.STOR_PLC = data["STOR_PLC(0=in the Fog,1=in the BC)"]

    def create_tasks(self, num_of_task_per_user, blockchain_function, list_of_end_users):
        if blockchain_function == 1:
            self.__apply_first_functionality(num_of_task_per_user, blockchain_function)
        if blockchain_function == 2:
            self.__apply_second_functionality(num_of_task_per_user, blockchain_function)
        if blockchain_function == 3:
            self.__apply_third_functionality(num_of_task_per_user, list_of_end_users, blockchain_function)
        if blockchain_function == 4:
            self.__apply_forth_functionality(blockchain_function)

    def send_tasks(self, list_of_fog_nodes):
        for obj in list_of_fog_nodes:
            if obj.address == self.addressParent:
                obj.receive_tasks(self.tasks, self.addressSelf)
                break

    def __apply_first_functionality(self, num_of_task_per_user, blockchain_function):
        for _ in range(num_of_task_per_user):
            self.tasks.append([random.randint(0, 1000000), blockchain_function])
        output.txs_success(num_of_task_per_user, self.addressParent, self.addressSelf)

    def __apply_second_functionality(self, num_of_task_per_user, blockchain_function):
        operations = ['+', '-', '*', '/']
        for _ in range(num_of_task_per_user):
            operation = random.choice(operations)
            random_computational_task = str(randrange(1000000)) + operation + str(randrange(1000000))
            self.tasks.append([self.addressParent, self.addressSelf, random_computational_task, blockchain_function])

    def __apply_third_functionality(self, num_of_task_per_user, list_of_end_users, blockchain_function):
        for _ in range(num_of_task_per_user):
            payment = randrange(round(data["Max_enduser_payment"], 0))
            receiver = random.choice(list_of_end_users)
            receiver_parent_address = receiver.addressParent
            receiver_individual_address = receiver.addressSelf
            proposed_transaction = [payment, self.addressParent, self.addressSelf, receiver_parent_address,
                                    receiver_individual_address, blockchain_function]
            self.tasks.append(proposed_transaction)

    def __apply_forth_functionality(self, blockchain_function):
        add_new_attributes(self)
        proposed_transaction = [self.addressParent, self.addressSelf, self.identity_added_attributes, blockchain_function]
        self.tasks.append(proposed_transaction)


def add_new_attributes(user):
    for key in user.identity_added_attributes:
        user.identity_added_attributes[key] = input(f"{str(user.addressParent)}.{str(user.addressSelf)}: {key}>> ")
