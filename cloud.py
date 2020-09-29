import random


class Cloud:

    def __init__(self):
        self.vms = list()

    def create_vms(self, data):
        print("The processor's computational power of the available VMs: ")
        for i in range(data.num_vms):
            self.vms.append((random.randint(data.minimum_capacity_of_vm, data.maximum_capacity_of_vm)))
            print("VR number (" + str(i + 1) + "): " + str(self.vms[i]))

    def send_vms(self, tcp):
        tcp.receive_vms(vms=self.vms)
