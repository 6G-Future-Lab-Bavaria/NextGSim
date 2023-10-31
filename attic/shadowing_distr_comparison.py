import numpy as np
import matplotlib.pyplot as plt

shadowing_std_los = 4
shadowing_std_nlos = 8

standart_normal_dis_samples = np.random.normal(size=1000)
shadowing_los = shadowing_std_los * standart_normal_dis_samples
shadowing_nlos = shadowing_std_nlos * standart_normal_dis_samples

plt.hist(shadowing_los, label="Normal LoS", color='orange')
plt.legend()
plt.show()
plt.hist(shadowing_nlos, label="Normal NO LoS", color='red')
plt.legend()
plt.show()

log_normal_dis_samples = np.random.lognormal(size=1000)
shadowing_los = shadowing_std_los * log_normal_dis_samples
shadowing_nlos = shadowing_std_nlos * log_normal_dis_samples

plt.hist(shadowing_los, label="Log-normal LoS", color='green')
plt.legend()
plt.show()
plt.hist(shadowing_nlos, label="Log-normal NO LoS", color='blue')
plt.legend()
plt.show()
