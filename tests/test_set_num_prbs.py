from runtime.SimulationParameters import SimulationParameters


def test_num_PRBs_and_mu():
    # FR 1
    subcarrier_spacing = [15, 30]  # kHz
    bandwidth = [5, 50]  # MHz
    mu_list = [0, 1]
    num_PRBs = [25, 133]
    for subcar, bw, mu, num_prb in zip(subcarrier_spacing, bandwidth, mu_list, num_PRBs):
        sim_params = SimulationParameters()
        sim_params.scenario.subcarrier_spacing = subcar
        sim_params.bandwidth_macro = bw
        sim_params.set_num_PRBs()
        assert sim_params.num_PRBs_macro == num_prb
        assert sim_params.mu == mu


test_num_PRBs_and_mu()