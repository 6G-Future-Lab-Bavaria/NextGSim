import os
import csv
import statistics as st
import matplotlib.pyplot as plt
import numpy as np
import collections

latency_results_file = "latency_analysis/latency_analysis_2022_12_14-10_40.csv"
file_data = open(latency_results_file)
csv_reader = csv.reader(file_data)

SHOW_UPLINK = True

processes = {}
rows = []
for row in csv_reader:
    rows.append(row)

for i in range(len(rows) - 1):
    tmp_row = rows[i + 1]
    user_id = int(tmp_row[2])
    if user_id not in processes.keys():
        processes[user_id] = {'ul_latency': [], 'backhaul_latency': [], 'processing_latency': [], 'timestamps': []}
    processes[user_id]['ul_latency'].append(float(tmp_row[4]))
    # processes[tmp_row[2]]['backhaul_latency'].append(float(tmp_row[5]))
    processes[user_id]['backhaul_latency'].append(float(2))
    processes[user_id]['processing_latency'].append(float(tmp_row[6]))
    processes[user_id]['timestamps'].append(float(tmp_row[7]))

processes = collections.OrderedDict(sorted(processes.items()))
users = []
average_ul_latencies = []
average_backhaul_latencies = []
average_processing_latencies = []
for user in processes.keys():
    users.append(user)
    average_ul_latencies.append(st.mean(processes[user]["ul_latency"]))
    average_backhaul_latencies.append(st.mean(processes[user]["backhaul_latency"]))
    average_processing_latencies.append(st.mean(processes[user]["processing_latency"]))

<<<<<<< Updated upstream
fig, (ax1, ax2) = plt.subplots(2, 2)
=======
fig, (ax1, ax2) = plt.subplots(2, 1)
>>>>>>> Stashed changes
fig.set_size_inches(18.5, 10.5)

# ------------------------------- aX1 [0] -------------------------------
width = 0.27
ind = np.arange(len(users))
rects1 = None
if SHOW_UPLINK:
<<<<<<< Updated upstream
    rects1 = ax1[0].bar(ind, average_ul_latencies, width, color='r')
rects2 = ax1[0].bar(ind + width, average_backhaul_latencies, width, color='g')
rects3 = ax1[0].bar(ind + width * 2, average_processing_latencies, width, color='b')

ax1[0].set_ylabel('Latency(ms)')
ax1[0].set_xlabel('Users')
ax1[0].set_title('Average Latencies')
ax1[0].set_xticks(ind + width)
ax1[0].set_xticklabels(users)
if SHOW_UPLINK:
    ax1[0].legend((rects1[0], rects2[0], rects3[0]),
                  ('Average UL Latency', 'Average Backhaul Latency', 'Average Processing Latency'))
else:
    ax1[0].legend((rects2[0], rects3[0]), ('Average Backhaul Latency', 'Average Processing Latency'))

# ------------------------------- aX1 [1] -------------------------------
ax1[1].set_ylabel('Processing Latency(ms)')
ax1[1].set_xlabel('Time(ms)')
ax1[1].set_title('Processing Latency Over Time')
for user in processes.keys():
    ax1[1].plot(processes[user]['timestamps'], processes[user]['processing_latency'], label=user)
leg = ax1[1].legend(title='Users', loc='upper right', bbox_to_anchor=(1.25, 1), ncol=2)

# ------------------------------- aX2 [0] -------------------------------
ax2[0].set_ylabel('UL Latency(ms)')
ax2[0].set_xlabel('Time(ms)')
ax2[0].set_title('UL Latency Over Time')
for user in processes.keys():
    ax2[0].plot(processes[user]['timestamps'], processes[user]['ul_latency'], label=user)
leg = ax2[0].legend(title='Users', loc='upper right', bbox_to_anchor=(-0.07, 1), ncol=2)

# ------------------------------- aX2 [1] -------------------------------
ax2[1].set_ylabel('Backhaul Latency(ms)')
ax2[1].set_xlabel('Time(ms)')
ax2[1].set_title('Backhaul Latency Over Time')
for user in processes.keys():
    ax2[1].plot(processes[user]['timestamps'], processes[user]['backhaul_latency'], label=user)
leg = ax2[1].legend(title='Users', loc='upper right', bbox_to_anchor=(1.25, 1), ncol=2)
=======
    rects1 = ax1.bar(ind, average_ul_latencies, width, color='r')
rects2 = ax1.bar(ind + width, average_backhaul_latencies, width, color='g')
rects3 = ax1.bar(ind + width * 2, average_processing_latencies, width, color='b')

ax1.set_ylabel('Latency(ms)')
ax1.set_xlabel('Users')
ax1.set_title('Average Latencies')
ax1.set_xticks(ind + width)
ax1.set_xticklabels(users)
if SHOW_UPLINK:
    ax1.legend((rects1[0], rects2[0], rects3[0]),
                  ('Average UL Latency', 'Average Backhaul Latency', 'Average Processing Latency'))
else:
    ax1.legend((rects2[0], rects3[0]), ('Average Backhaul Latency', 'Average Processing Latency'))

# ------------------------------- aX1 [1] -------------------------------
# ax1[1].set_ylabel('Processing Latency(ms)')
# ax1[1].set_xlabel('Time(ms)')
# ax1[1].set_title('Processing Latency Over Time')
# for device in processes.keys():
#     ax1[1].plot(processes[device]['timestamps'], processes[device]['processing_latency'], label=device)
# leg = ax1[1].legend(title='Users', loc='upper right', bbox_to_anchor=(1.25, 1), ncol=2)

# ------------------------------- aX2 [0] -------------------------------
ax2.set_ylabel('UL Latency(ms)')
ax2.set_xlabel('Time(ms)')
ax2.set_title('UL Latency Over Time')
for user in processes.keys():
    ax2.plot(processes[user]['timestamps'], processes[user]['ul_latency'], label=user)
leg = ax2.legend(title='Users', loc='upper right', bbox_to_anchor=(-0.03, 1), ncol=2)

# ------------------------------- aX2 [1] -------------------------------
# ax2[1].set_ylabel('Backhaul Latency(ms)')
# ax2[1].set_xlabel('Time(ms)')
# ax2[1].set_title('Backhaul Latency Over Time')
# for device in processes.keys():
#     ax2[1].plot(processes[device]['timestamps'], processes[device]['backhaul_latency'], label=device)
# leg = ax2[1].legend(title='Users', loc='upper right', bbox_to_anchor=(1.25, 1), ncol=2)
>>>>>>> Stashed changes

# --------------------------------------- -------------------------------
plt.show()
