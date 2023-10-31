from gnb.ThroughputCalculation import ThroughputCalculation
from runtime.Simulation import Simulation

NUM_CELLS = 2
NUM_USERS = 5


class TestThroughputCalculation:
    def __init__(self):
        self.simulation = Simulation()

    def test_throughput_calculation_dl_for_different_mimo(self):
        self.simulation.sim_params.scenario.subcarrier_spacing = 15
        self.simulation.sim_params.bandwidth_macro = 5
        throughput_calculator = ThroughputCalculation(self.simulation)
        throughput_calculator.j = 1
        throughput_calculator.Rmax = 0.92578125
        throughput_calculator.f = 1
        throughput_calculator.mu = 0  # BW 5MHz, FR1, 15 kHz
        qm = 6  # 64QAM
        assert self.simulation.sim_params._set_num_PRBs == 25
        num_PRBs = self.simulation.sim_params._set_num_PRBs  # 25
        overhead = 0.14
        res_rates = [20, 20*4, 20*8+1]
        for v, res in zip([1, 4, 8], res_rates):
            throughput_calculator.v = v
            data_rate = throughput_calculator.calc_data_rate(qm, num_PRBs, overhead)
            assert round(data_rate, 0) == res  # MHz

    def test_throughput_calculation_dl_for_different_modulations(self):
        self.simulation.sim_params.scenario.subcarrier_spacing = 15
        self.simulation.sim_params.bandwidth_macro = 5
        throughput_calculator = ThroughputCalculation(self.simulation)
        throughput_calculator.j = 1
        throughput_calculator.Rmax = 0.92578125
        throughput_calculator.f = 1
        throughput_calculator.mu = 0  # BW 5MHz, FR1, 15 kHz
        throughput_calculator.v = 1
        assert self.simulation.sim_params._set_num_PRBs == 25
        num_PRBs = self.simulation.sim_params._set_num_PRBs  # 25
        overhead = 0.14
        res_rates = [6.7, 13.4, 20.1, 26.8]
        for qm, res in zip([2, 4, 6, 8], res_rates):
            data_rate = throughput_calculator.calc_data_rate(qm, num_PRBs, overhead)
            assert round(data_rate, 1) == res  # MHz

    def test_throughput_calculation_ul_1(self):
        self.simulation.sim_params.scenario.subcarrier_spacing = 15
        self.simulation.sim_params.bandwidth_macro = 5
        throughput_calculator = ThroughputCalculation(self.simulation)
        throughput_calculator.j = 1
        throughput_calculator.Rmax = 0.92578125
        throughput_calculator.f = 1
        throughput_calculator.mu = 0  # BW 50MHz, FR1, 30 kHz
        throughput_calculator.v = 4
        assert self.simulation.sim_params._set_num_PRBs == 25
        num_PRBs = self.simulation.sim_params._set_num_PRBs
        overhead = 0.08
        qm = 6
        data_rate = throughput_calculator.calc_data_rate(qm, num_PRBs, overhead)
        assert round(data_rate, 1) == 85.9  # MHz

    def test_throughput_calculation_ul_2(self):
        self.simulation.sim_params.scenario.subcarrier_spacing = 30
        self.simulation.sim_params.bandwidth_macro = 50
        throughput_calculator = ThroughputCalculation(self.simulation)
        throughput_calculator.mu = 1  # BW 50MHz, FR1, 30 kHz
        throughput_calculator.j = 1
        throughput_calculator.Rmax = 0.92578125
        throughput_calculator.f = 1
        throughput_calculator.v = 4
        # print(self.ran_simulation.sim_params.num_PRBs)
        num_PRBs = 133  # self.ran_simulation.sim_params.num_PRBs
        overhead = 0.08
        qm = 6
        assert throughput_calculator.ts_mu_s == 0.00003571428571428572
        data_rate = throughput_calculator.calc_data_rate(qm, num_PRBs, overhead)
        assert round(data_rate, 1) == 913.5  # MHz


def main():
    test = TestThroughputCalculation()
    test.test_throughput_calculation_dl_for_different_mimo()
    test.test_throughput_calculation_dl_for_different_modulations()
    test.test_throughput_calculation_ul_1()
    test.test_throughput_calculation_ul_2()
    print("done")


if __name__ == "__main__":
    main()
