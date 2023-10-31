from collections import defaultdict


def count_num_ping_pong_handovers(gnbs, window):
    unique_gnbs = [gnbs[0]]
    # unique_gnbs_ttt = [0]
    gnb_to_time_dict = defaultdict(list)
    for t in range(len(gnbs)):
        if gnbs[t] != unique_gnbs[-1] or t == 0:
            unique_gnbs.append(gnbs[t])
            # unique_gnbs_ttt.append(t)
            gnb_to_time_dict[gnbs[t]].append(t)

    # print(unique_gnbs)
    # print(unique_gnbs_ttt)
    # print(gnb_to_time_dict)

    num_ping_pong_handovers = 0
    for gnb in gnb_to_time_dict:
        # num_ping_pong_handovers += (len(gnb_to_time_dict[gnb]) - 1)
        for i in range(len(gnb_to_time_dict[gnb])-1):
            if gnb_to_time_dict[gnb][i+1] - gnb_to_time_dict[gnb][i] <= window:
                num_ping_pong_handovers += 1

    return num_ping_pong_handovers


window = 18
gnbs_1 = [1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 5, 5, 1, 1, 1, 2, 2, 2]
gnbs_2 = [10, 10, 10, 10, 10, 5, 5, 5, 5, 5, 5, 5, 7, 7, 7, 7, 7, 7, 10, 10, 10, 10]
res_num_ping_pong = [3, 1]
for gnbs, res in zip([gnbs_1, gnbs_2], res_num_ping_pong):
    num_ping_pong_handovers = count_num_ping_pong_handovers(gnbs, window)
    assert num_ping_pong_handovers == res

window = 10
res_num_ping_pong = [2, 0]
for gnbs, res in zip([gnbs_1, gnbs_2], res_num_ping_pong):
    num_ping_pong_handovers = count_num_ping_pong_handovers(gnbs, window)
    print(f"Number of ping pong handovers {num_ping_pong_handovers}")
    assert num_ping_pong_handovers == res


# gnbs = gnbs_2
# num_ping_pong_handovers = count_num_ping_pong_handovers(gnbs, window)
# print(f"Number of ping pong handovers {num_ping_pong_handovers}")
