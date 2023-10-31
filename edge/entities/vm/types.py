from entities.vm.vm import Vm


class Vm1(Vm):
    def __init__(self, name="vm1", num_of_cpus=1, storage=10 ** 9, bw=10 ** 9):
        super().__init__(name=name, num_of_cpus=num_of_cpus, storage=storage, bw=bw)
