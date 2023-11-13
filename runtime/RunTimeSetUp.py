import numpy as np
import pandas as pd


class RunTime:
    def __init__(self, simulation):
        self.sim = simulation
        self.sim_params = self.sim.sim_params

    def gen_user_task(self):
        devices = self.sim.devices_per_scenario
        user_packet_data = []
        user_packet_cycles = []
        user_packet_delay = []
        for device in devices:
            user_packet_data.append(np.random.randint(low=device.app.data_size_min, high=device.app.data_size_max))
            user_packet_cycles.append(np.random.uniform(low=device.app.cycles_per_bit_min, high=device.app.cycles_per_bit_max))
            user_packet_delay.append(np.random.randint(low=device.app.delay_min, high=device.app.delay_max))
        return user_packet_data, user_packet_cycles, user_packet_delay

    def write_RAN_to_DF(self, BS_per_UE, user_throughput, transmission_latency, packets_data, packets_cycles,
                        packets_delays):
        # utility.set_path()
        RAN_to_MEC_inf = np.column_stack(
            (BS_per_UE, user_throughput, transmission_latency, packets_data, packets_cycles, packets_delays))
        df = pd.DataFrame(RAN_to_MEC_inf, columns=['BS', 'Throughput[Kbit/s]', 'Latency[ms]', 'Packet data size[bits]',
                                                   'Packet cycles per bit[cycles/bit]', 'Packet delay[ms]'])
        # Its is expected to overwrite the csv file
        # df.to_csv('RAN_MEC.csv', index=True)
        return df

    def write_RAN_information(self, SNR, over_time=True):
        shape = SNR.shape
        columns = ['BS', 'UE', 'PRB']
        index = pd.MultiIndex.from_product([range(s) for s in shape], names=columns)
        df_stacked = ['BS', 'UE', 'PRB']
        df = pd.DataFrame({'SNR': SNR.flatten()}, index=index).reset_index()
        df.to_csv('RAN_information.csv', mode='a', index=False)

    def read_RAN_information(self):
        df = pd.read_csv('RAN_information.csv')
        FIELD_TO_SEARCH = 'BS'
        # VALUE_TO_MATCH_FIELD = 'Line'
        # header_indices = df.index[df[FIELD_TO_SEARCH] == VALUE_TO_MATCH_FIELD].tolist()
        header_indices = df.index[pd.to_numeric(df[FIELD_TO_SEARCH], errors='coerce').isna()].tolist()
        # Add one row past the end so we can have a stopping point later
        header_indices.append(df.shape[0] + 1)

        # Preallocate output df list with the first chunk (using existing headers).
        list_of_dfs = [df.iloc[0:header_indices[0]]]

        if len(header_indices) > 1:
            for idx in range(len(header_indices) - 1):
                # Extract new header
                header_index = header_indices[idx]
                next_header_index = header_indices[idx + 1]
                current_header = df.iloc[[header_index]].values.flatten().tolist()

                # Make a df from this chunk
                current_df = df[header_index + 1:next_header_index].to_numpy()[:, 3].reshape((1, 20, 6))
                # Apply the new header
                current_df.columns = current_header
                current_df.reset_index(drop=True, inplace=True)
                list_of_dfs.append(current_df)

        # Show output
        for df_index, current_df in enumerate(list_of_dfs):
            print("DF chunk index: {}".format(df_index))
            print(current_df)
