# @Author: Polina Kutsevol
# @Date: 2021-04-12
# @Email: kutsevol.pn@phystech.edu
# @Last modified by: Polina Kutsevol

class Controller:
    def __init__(self, simulation, ID, x, y):
        self.simulation = simulation
        self.ID = ID
        self.x = x
        self.y = y
        self.gnbs = []
        self.available_resources = 0

    def connect_gnb(self, gnb):
        self.gnbs.append(gnb)
        self.available_resources += gnb.init_available_resources()

    def disconnect_gnb(self, gnb):
        self.gnbs.remove(gnb)
        self.available_resources -= gnb.init_available_resources()