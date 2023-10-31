import numpy as np
from scipy.stats import poisson
import seaborn as sns
import matplotlib.pyplot as plt
from skimage import filters


data_poisson = poisson.rvs(mu=2*10**(-4), size=1000**2)
poisson_array = data_poisson.reshape(1000, 1000)
poisson_array = filters.gaussian(poisson_array, sigma=1)
plt.imshow(poisson_array > np.median(poisson_array), cmap="gray")
plt.xlabel("X")
plt.ylabel("Y")
plt.show()
print(f"Number of blockages is {sum(data_poisson)}")
blockages = np.where(data_poisson == 0)
print(blockages)
print(blockages.shape)

