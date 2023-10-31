from runtime.Simulation import Simulation

config = {'always_los_flag': False,
          'handover_algorithm': 'Normal'}


error_prob_list = [0.0, 0.2, 0.5, 0.7, 0.9]
for error_prob in error_prob_list:
    config['error_probability'] = error_prob
    simulation = Simulation(config)

    simulation.run_RANsimulationEnvironment()
assert 0, "Done"