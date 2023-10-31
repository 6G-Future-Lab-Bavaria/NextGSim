import numpy as np
import matplotlib.pyplot as plt


# This channel was used in Prediction-based CHO for 5G mm-wave networks
class mmWaveChannel:
    def __init__(self):
        self.shadowing_los = 5.8  # dB
        self.shadowing_nlos = 8.7  # dB

    def calc_pathloss(self, d, los_flag):
        if los_flag:
            return 61.4 + 20*np.log10(d)
        else:
            return 72.0 + 29.2 * np.log10(d)

    def calc_shadowing(self, los_flag, size=1):
        s = np.random.lognormal(size=size)
        if los_flag:
            return s * self.shadowing_los
        else:
            return s * self.shadowing_nlos

    def plot_pathloss(self):
        for los_flag in [1, 0]:
            for d in range(10, 200, 10):
                if los_flag:
                    color = 'green'
                    label = 'LoS'
                else:
                    color = 'red'
                    label = 'NLoS'
                loss = self.calc_pathloss(d, los_flag)
                if d == 10:
                    plt.scatter(d, loss, color=color, label=label)
                else:
                    plt.scatter(d, loss, color=color)
        plt.legend()
        plt.title("mm-Wave pathloss")
        plt.xlabel("Meters")
        plt.ylabel("dB")
        plt.show()

    def plot_shadowing(self):
        for los_flag in [1, 0]:
            s = self.calc_shadowing(los_flag, size=1000)
            plt.hist(s, bins=30)
            plt.title(f"Log-normal shadowing LoS {los_flag}")
            plt.xlabel("dB")
            plt.show()


channel = mmWaveChannel()
channel.plot_pathloss()
channel.plot_shadowing()



