from edge.entities import EdgeServer


class EdgeServer1(EdgeServer):
    def __init__(self, cpu_clock_speed=2.1 * 10 ** 5, num_of_cpus=50, memory=32):
        super(EdgeServer1, self).__init__(cpu_clock_speed=cpu_clock_speed, num_of_cpus=num_of_cpus, memory=memory)


class EdgeServer2(EdgeServer):
    def __init__(self, cpu_clock_speed=4.2 * 10 ** 5, num_of_cpus=50, memory=32):
        super(EdgeServer2, self).__init__(cpu_clock_speed=cpu_clock_speed, num_of_cpus=num_of_cpus, memory=memory)


class EdgeServer3(EdgeServer):
    def __init__(self, cpu_clock_speed=8.4 * 10 ** 5, num_of_cpus=50, memory=32):
        super(EdgeServer3, self).__init__(cpu_clock_speed=cpu_clock_speed, num_of_cpus=num_of_cpus, memory=memory)
