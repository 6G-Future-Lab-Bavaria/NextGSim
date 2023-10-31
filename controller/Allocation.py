# @Author: Polina Kutsevol
# @Date: 2021-04-12
# @Email: kutsevol.pn@phystech.edu
# @Last modified by: Polina Kutsevol


import numpy as np
import matplotlib.pyplot as plt
import gurobipy as gp
import networkx as nx
from gurobipy import GRB
import seaborn as sns

sns.set_style("ticks", {"xtick.major.size": 8, "ytick.major.size": 8})
sns.set_palette(sns.color_palette("CMRmap_r"))

c = 3e8


class Optimization(object):

    def __init__(self, B_len, C_len):
        self.B_len = B_len
        #self.C1_len = round(B_len / 30.0)
        self.C1_len = C_len
        # self.C2_len = 1
        self.C2_len = 0
        self.U = np.zeros(B_len)
        self.adj = None
        self.S = None
        self.l1 = 70 * 4
        self.l2 = 70 * 100
        self.w1 = 0
        self.w2 = 0
        self.w3 = 1
        self.w4 = 0
        self.colors = []
        for i in range(self.C1_len + self.C2_len):
            self.colors.append('#%06X' % np.random.randint(0, 0xFFFFFF))
        self.delay_coeffs = [1.88909258e-03, 7.08122015e-06, 3.01722544e-07]
        self.delay_coeffs_1 = [5.46287554e+00, 1.86056548e-01, 1.02384615e-03]
        self.cpu_usage_coeffs = [2.41672459e+01, 4.56237176e-01, 1.61165848e-02]
        self.dist_matrix = np.zeros((self.B_len, self.C1_len + self.C2_len))
        self.m = gp.Model("assignment")
        self.x = np.empty((self.B_len, self.C1_len + self.C2_len), gp.Var)
        self.y = np.empty((self.C1_len + self.C2_len), gp.Var)
        self.C1 = ["c" + str(i) for i in range(self.C1_len)]
        #self.C2 = ["cu0", "cu1", "cu2"]
        self.C2 = []
        self.C = self.C1 + self.C2
        self.B = ["b" + str(i) for i in range(self.B_len)]
        self.S_gr = self.C2 + self.B + self.C1
        self.d = np.zeros((self.C1_len + self.C2_len + self.B_len, self.C1_len + self.C2_len + self.B_len))
        self.x_hist = []
        self.x_prev = np.zeros((self.B_len, self.C1_len + self.C2_len))
        self.init_delay_arr = []
        self.prop_delay_arr = []
        self.n_of_ctrls_arr = []
        self.migr_delay = []
        self.best_controllers = np.zeros(self.B_len, dtype=np.int)

    def set_weights(self, weights):
        self.w1, self.w2, self.w3, self.w4 = weights

    def get_network(self, coordinates, best_controllers):
        #C2 = pd.DataFrame([(1200, 1800), (700, 1500), (1100, 700)])
        #B = pd.read_csv('cG.csv', names=[0, 1])
        #C1 = pd.read_csv('cSw.csv', names=[0, 1])
        #A = np.array(range(self.B_len + self.C1_len + 1))
        #adj_tmp = pd.read_csv('adj.csv', names=A)
        #S = pd.concat([C2, B, C1])
        #self.S = S.reset_index()
        self.S = coordinates

        #adj_tmp = adj_tmp.to_numpy()
        #self.adj = np.zeros((adj_tmp.shape[0] - 1 + self.C2_len, adj_tmp.shape[0] - 1 + self.C2_len))
        self.adj = np.zeros((self.B_len + self.C1_len, self.B_len + self.C1_len))
        #self.adj[3:, 3:] = adj_tmp[1:, 1:]
        for i in range(self.C1_len + self.C2_len + self.B_len):
            for j in range(self.C1_len + self.C2_len + self.B_len):
                if (self.S_gr[i][0] == 'c' and self.S_gr[j][0] == 'c'):
                    self.adj[i][j] = 1
                    self.adj[j][i] = 1
        for i in range(self.B_len):
            self.adj[i][self.B_len+best_controllers[i]] = 1
            self.adj[self.B_len+best_controllers[i]][i] = 1

    def get_shortest_paths(self):
        for i in range(self.C1_len + self.C2_len + self.B_len):
            for j in range(self.C1_len + self.C2_len + self.B_len):
                self.d[i][j] = self.adj[i][j] * np.sqrt(
                    (self.S[0][i] - self.S[0][j]) ** 2 + (self.S[1][i] - self.S[1][j]) ** 2)

        G = nx.Graph()
        G.add_nodes_from(self.C)
        G.add_nodes_from(self.B)
        for i in range(self.C1_len + self.C2_len + self.B_len):
            for j in range(self.C1_len + self.C2_len + self.B_len):
                if self.adj[i][j] != 0:
                    G.add_edge(self.S_gr[i], self.S_gr[j], dist=self.d[i][j])

        for i in range(self.B_len):
            for j in range(self.C1_len + self.C2_len):
                self.dist_matrix[i][j] = nx.shortest_path_length(G, self.B[i], self.C[j], weight="dist")

    def delay(self, bss, users):
        return np.dot(np.array([bss * 0 + 1, bss, users]).T, self.delay_coeffs)

    def cpu_usage(self, bss, users):
        return 4 * np.dot(np.array([bss * 0 + 1, bss, users]).T, self.cpu_usage_coeffs)

    def delay1(self, bss, users, c):
        if self.cpu_usage(bss, users) <= self.l1:
            return np.dot(np.array([bss * 0 + 1, bss, users]).T, self.delay_coeffs)
        elif self.cpu_usage(bss, users) <= self.l2 and c[1] == 'u':
            return np.dot(np.array([bss * 0 + 1, bss, users]).T, self.delay_coeffs)
        else:
            return np.dot(np.array([bss * 0 + 1, bss, users]).T, self.delay_coeffs_1)

    def set_optimization_params(self):
        self.m = gp.Model("assignment")
        self.m.params.IterationLimit = 1000
        self.m.params.MIPGap = 1.5 * 10e-2
        self.x = np.empty((self.B_len, self.C1_len + self.C2_len), gp.Var)
        self.y = np.empty((self.C1_len + self.C2_len), gp.Var)
        for i in range(self.B_len):
            for j in range(self.C1_len + self.C2_len):
                self.x[i][j] = self.m.addVar(vtype=GRB.BINARY, name="x_" + str(i) + "_" + str(j))
        for j in range(self.C1_len + self.C2_len):
            self.y[j] = self.m.addVar(vtype=GRB.BINARY, name="y_" + str(j))
        A = np.ones((self.B_len, self.C1_len + self.C2_len)) - self.x_prev
        sum_delay = gp.quicksum((self.x[k][j] * self.delay(gp.quicksum(self.x[:, j]), gp.quicksum(
            [self.x[i][j] * self.U[i] for i in range(self.B_len)])) for j in range(self.C1_len + self.C2_len) for k in
                                 range(self.B_len)))
        migr_delay = gp.quicksum((A[i][j] * self.x[i][j] * self.delay(gp.quicksum(self.x[:, j]), gp.quicksum(
            [self.x[k][j] * self.U[k] for k in range(self.B_len)])) for i in range(self.B_len) for j in
                                  range(self.C1_len + self.C2_len)))
        sum_prop_delay = 1 / c * gp.quicksum((self.x[i][j] * self.dist_matrix[i][j] for i in range(self.B_len) for j in
                                              range(self.C1_len + self.C2_len)))
        obj = self.w1 * (sum_delay) / (self.B_len * 0.002) + self.w3 * (sum_prop_delay) / (
                    (self.B_len) * 0.000001) + self.w2 * gp.quicksum(self.y) / (
                          self.C1_len + self.C2_len) + self.w4 * migr_delay / (100 * 0.002)

        self.m.setObjective(obj, GRB.MINIMIZE)

        for i in range(self.B_len):
            self.m.addConstr(np.sum(self.x[i]) == 1)

        for i in range(self.B_len):
            for j in range(self.C1_len + self.C2_len):
                self.m.addConstr(self.x[i][j] - self.y[j] <= 0)
        for i in range(self.C1_len):
            self.m.addConstr(self.cpu_usage(gp.quicksum(self.x[:, i]), gp.quicksum(
                [self.x[j][i] * self.U[j] for j in range(self.B_len)])) <= self.l1)
        for i in range(self.C2_len):
            self.m.addConstr(self.cpu_usage(gp.quicksum(self.x[:, self.C1_len + i]), gp.quicksum(
                [self.x[j][self.C1_len + i] * self.U[j] for j in range(self.B_len)])) <= self.l2)

    def initiate_alloc(self, coordinates, best_controllers):
        self.get_network(coordinates, best_controllers)
        self.get_shortest_paths()

    def set_seed(self, s):
        np.random.seed(s)

    def perform_alloc(self, U):
        self.U = U
        self.set_optimization_params()
        self.m.optimize()
        for i in range(self.B_len):
            for j in range(self.C1_len):
                if int(self.x[i][j].x) == 1:
                    self.best_controllers[i] = j

    def plot(self):

        # self.count_metrics(self.U)
        alloc = {}
        for j in range(self.C1_len + self.C2_len):
            alloc[self.C[j]] = self.colors[j]
        for i in range(self.B_len):
            for j in range(self.C1_len + self.C2_len):
                alloc[self.B[i]] = "k"
        for i in range(self.B_len):
            for j in range(self.C1_len + self.C2_len):
                if int(self.x[i][j].x) == 1:
                    # print("-----")
                    # print(i, j)
                    alloc[self.B[i]] = self.colors[j]

        A = nx.Graph()
        for i in range(self.C2_len):
            A.add_node(self.C2[i], color=alloc[self.C2[i]], size=500)
        for i in range(self.B_len):
            A.add_node(self.B[i], color=alloc[self.B[i]], size=150)
        for i in range(self.C1_len):
            A.add_node(self.C1[i], color=alloc[self.C[i]], size=300)

        for i in range(self.C1_len + self.C2_len + self.B_len):
            for j in range(self.C1_len + self.C2_len + self.B_len):
                if self.adj[i][j] != 0:
                    A.add_edge(self.S_gr[i], self.S_gr[j], minlen=self.d[i][j])
        pos = {self.S_gr[i]: tuple((self.S.loc[i][0], self.S.loc[i][1])) for i in
               range(self.C1_len + self.C2_len + self.B_len)}
        plt.figure(1, figsize=(12, 12))
        nx.draw(A, pos, with_labels=True, node_color=[A.node[node]["color"] for node in A],
                node_size=[A.node[node]["size"] for node in A], alpha=0.7, font_size=16)
        # plt.savefig("MILP.pdf")
        # plt.show()

    def count_metrics(self, U):
        self.U = U
        x_v = np.zeros((self.B_len, self.C1_len + self.C2_len), int)
        for i in range(self.B_len):
            for j in range(self.C1_len + self.C2_len):
                x_v[i][j] = self.x[i][j].x

        self.x_hist.append(x_v)
        y_v = np.zeros((self.C1_len + self.C2_len), int)
        for j in range(self.C1_len + self.C2_len):
            y_v[j] = self.y[j].x

        A = np.ones((self.B_len, self.C1_len + self.C2_len)) - self.x_prev
        sum_delay = np.sum((x_v[k][j] * self.delay1(np.sum(x_v[:, j]),
                                                    np.sum([x_v[i][j] * self.U[i] for i in range(self.B_len)]),
                                                    self.C[j]) for j in range(self.C1_len + self.C2_len) for k in
                            range(self.B_len)))
        sum_prop_delay = 1 / c * np.sum(
            (x_v[i][j] * self.dist_matrix[i][j] for i in range(self.B_len) for j in range(self.C1_len + self.C2_len)))
        migr_delay = np.sum((A[i][j] * x_v[i][j] * self.delay1(np.sum(x_v[:, j]), np.sum(
            [x_v[k][j] * self.U[k] for k in range(self.B_len)]), self.C[j]) for i in range(self.B_len) for j in
                             range(self.C1_len + self.C2_len)))
        self.init_delay_arr.append(sum_delay / (self.B_len))
        self.prop_delay_arr.append(sum_prop_delay / self.B_len)
        self.n_of_ctrls_arr.append(np.sum(y_v))
        self.migr_delay.append(migr_delay)
        print(self.w1 * (sum_delay) / ((0.002 * self.B_len)))
        print(self.w3 * (sum_prop_delay) / (self.B_len * 0.000001))
        print(self.w2 * np.sum(y_v) / (self.C1_len + self.C2_len))
        print(self.w4 * self.w4 * migr_delay / (100 * 0.002))
        for i in range(self.C1_len + self.C2_len):
            print(self.cpu_usage(np.sum(x_v[:, i]), np.sum([x_v[j][i] * self.U[j] for j in range(self.B_len)])))
        # for j in range(self.B_len):
        #    print(np.sum(x_v[j]))
        self.x_prev = x_v

    def get_B(self):
        return self.B_len




