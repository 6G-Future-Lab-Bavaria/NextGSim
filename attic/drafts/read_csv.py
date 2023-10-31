import csv
from random import randint

csv_file_test = '../csv_files/RAN_MEC_v2.csv'


def read_ran_data_from_csv(csv_file):
    """

    Args:
        csv_file: Location of the file that is containing the RAN.csv side information

    Returns: A tuple of (device ids, attached base stations, throughputs, latencies)

    """
    file = open(csv_file)
    csvreader = csv.reader(file)
    rows = []

    for row in csvreader:
        rows.append(row)

    user_ids = []
    attached_base_stations = []
    throughputs = []
    latencies = []
    packet_data_sizes = []
    packet_cycles_per_bit = []
    packet_delay_tolerances = []
    for i in range(len(rows)-1):
        tmp_row = rows[i + 1]
        user_ids.append(tmp_row[0])
        attached_base_stations.append(tmp_row[1])
        attached_base_stations.append(randint(0, 9))
        throughputs.append(tmp_row[2])
        latencies.append(tmp_row[3])
        packet_data_sizes.append(tmp_row[4])
        packet_cycles_per_bit.append(tmp_row[5])
        packet_delay_tolerances.append(tmp_row[6])

    return user_ids, attached_base_stations, throughputs, latencies, packet_data_sizes, packet_cycles_per_bit, packet_delay_tolerances

user_ids, attached_base_stations, throughputs, latencies, packet_data_sizes, packet_cycles_per_bit, packet_delay_tolerances = read_ran_data_from_csv(csv_file_test)
