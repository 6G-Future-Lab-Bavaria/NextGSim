import numpy as np
from gnb.ConditionalHandover import ConditionalHandover


class AHPHandover(ConditionalHandover):
    def __init__(self):
        # super().__init__(ran_simulation)
        self.importance = {(0,1): 2, (0,2): 3, (1,2): 3/2} # how important is option {} over option {}
        self.criteria = ['QoS', 'RSRP', 'Probability']
        # options are {0: QoS, 1: RSRP, 2: Probability of Connection}
        self.p = self.calc_priority_vector(self.calc_comparison_matrix())

    def check_if_execution_condition_is_satisfied(self, user, channel_matrix):
        # Find gNb with the best score, if UE is not yet connected to it, make a handover
        max_score = None
        best_gnb = None
        for prep_cell in user.prepared_gnbs:
            score = self.calc_gnb_score(user, prep_cell, channel_matrix)
            if max_score is None or score > max_score:
                max_score = score
                best_gnb = prep_cell
        if best_gnb.ID != user.my_gnb.ID:
            # make a handover
            current_time = self.simulation.TTI # * self.ran_simulation.sim_params.TTI_duration
            msg = f"3. Executing handover to prepared gNB {best_gnb.ID} for user {user.ID} at TTI={current_time}. My gNB is {user.my_gnb.ID}"
            self.print_msg(user, msg, 'magenta')
            user.prepared_gnbs[best_gnb] = True
            user.next_gnb = best_gnb
            self.execute_handover(user)
            return True
        else:
            return False # stay connected to my gNB

    def calc_comparison_matrix(self):
        n = len(self.importance)
        A = np.ones([n, n])
        for i in range(0, n):
            for j in range(0, n):
                if i < j:
                    aij = self.importance[(i, j)]
                    A[i, j] = float(aij)
                    A[j, i] = 1 / float(aij)
        print(f"Pair-wise comparison matrix: \n {A}")
        return A

    def calc_priority_vector(self, A):
        # eig_val = np.linalg.eig(A)[0].max()
        eig_vec = np.linalg.eig(A)[1][:, 0]
        p = eig_vec / eig_vec.sum()
        print(f"Priority vector {p} for criteria {self.criteria}")
        return p

    def calc_gnb_score(self, user, gnb, channel_matrix):
        # todo: normalize RSRP values and probability
        rsrp = channel_matrix[user.ID, gnb.ID]
        qos = 1  # todo
        probability = 1 / self.simulation.channel.distance_users_gnbs_3d[user.ID, gnb.ID]
        vector = np.array([qos, rsrp, probability])
        score = vector.dot(self.p)
        print(f"gNb {gnb.ID} has score {score}")
        return score


if __name__ == "__main__":
    handover = AHPHandover()
    matrix = handover.calc_comparison_matrix()
    p = handover.calc_priority_vector(matrix)
