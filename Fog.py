import mempool


class Fog:
    def __init__(self, address):
        self.address = address
        self.tasks = []
        self.list_of_connected_users = set()

    def receive_tasks(self, tasks, sender):
        self.tasks.extend(tasks)
        self.list_of_connected_users.add(sender)

    def send_tasks_to_BC(self):
        for i in range(len(self.tasks)):
            mempool.MemPool.put(self.tasks[i])
