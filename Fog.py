import random
import output
import mempool
import modification

data = modification.read_file("Sim_parameters.json")


class Fog:
    def __init__(self, address):
        self.address = address
        self.tasks = []
        self.list_of_connected_users = set()
        self.STOR_PLC = data["STOR_PLC(0=in the Fog,1=in the BC)"]
        self.local_storage = []

    def receive_tasks(self, tasks, sender):
        self.tasks.extend(tasks)
        self.list_of_connected_users.add(sender)

    def send_tasks_to_BC(self, user_informed):
        temporary_task = random.choice(self.tasks)
        if not user_informed:
            output.inform_of_fog_procedure(temporary_task[-1], self.STOR_PLC)
        if temporary_task[-1] == 1:
            for task in self.tasks:
                if self.STOR_PLC == 1:
                    mempool.MemPool.put(task)
                else:
                    self.local_storage.append(task)
        if temporary_task[-1] == 2:
            for task in self.tasks:
                for letter in task[-2]:
                    if letter in ['+', '-']:
                        result = eval(task[-2])
                        produced_transaction = ['End-user address: ' + str(task[0]) + '.' + str(task[1]),
                                                'Requested computational task: ' + str(task[2]), 'Result: '
                                                + str(result), "Performed_by_fog_node_num: " + str(self.address)]
                        self.local_storage.append(produced_transaction)
                        break
                    elif letter in ['/', '*']:
                        mempool.MemPool.put(task)
                        break

        if temporary_task[-1] == 3:
            for task in self.tasks:
                mempool.MemPool.put(task)
        if temporary_task[-1] == 4:
            self.local_storage.extend(self.tasks)
