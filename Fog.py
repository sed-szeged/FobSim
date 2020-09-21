import memPool


class Fog:
    def __init__(self, address):
        self.address = address
        self.tasks = []
        self.list_of_connected_users = set()

    def receive_tasks(self, tasks, sender):
        self.tasks.extend(tasks)
        self.list_of_connected_users.add(sender)

    def send_tasks_to_BC(self):
        print(self.tasks)
        for i in range(len(self.tasks)):
            memPool.MemPool.put(self.tasks[i])
