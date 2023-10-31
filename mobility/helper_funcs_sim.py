# @Author: Anna Prado
# @Date: 2020-11-15
# @Email: anna.prado@tum.de
# @Last modified by: Alba Jano


def generate_mob_traces_slaw(simulation):
    if simulation.sim_params.generate_mobility_traces:
        # TODO: Anna is it ok to keep the import here? I am having problems with the matlab module
        from mobility.GenerateMobility import GenerateMobility
        num_users = float(simulation.sim_params.scenario.max_num_devices_per_scenario)
        x_max = float(simulation.sim_params.scenario.x_max)
        y_max = float(simulation.sim_params.scenario.y_max)
        thours = float(simulation.sim_params.num_TTI)  # todo: TTIs to hours, and not measuring device speed at every TTI
        mob = GenerateMobility(num_users, x_max, y_max, thours)
        simulation.mobility_traces_filename = mob.genetate_mobility_traces()
    # else:
    #     ran_simulation.mobility_traces_filename = ran_simulation.sim_params.scenario.mobility_traces_filename
    #     if os.path.isfile(ran_simulation.mobility_traces_filename):
    #         pass
    #     else:
    #         raise NameError(f"File with mobility traces does not exist: {ran_simulation.mobility_traces_filename}. "
    #                         f"Provide another file name or set flag generate_mobility_traces in simparams to True")


# def read_mob_traces_slaw(ran_simulation):
#     time_steps = ran_simulation.sim_params.num_TTI  # fixme: from TTI to hours (How often do we want to update mobility?)
#     readmobility = ReadMobility(ran_simulation.mobility_traces_filename, time_steps, len(ran_simulation.devices_per_scenario))
#     ran_simulation.X_mobility, ran_simulation.Y_mobility, _ = readmobility.read_SLAW_output(len(ran_simulation.devices_per_scenario))
#     # if plot_SLAW:
#     #     readmobility.plot_mobility(ran_simulation.X_mobility, ran_simulation.Y_mobility,
#     #                                ran_simulation.sim_params.scenario.max_num_devices_per_cell)



