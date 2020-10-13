import pandas as pd
import numpy as np
import scipy.ndimage.filters as fil
import matplotlib.pyplot as plt

data = pd.read_csv('sensor_data_21-02.csv')
temp_data = [int(v) for v in data['data'][0][1:][:-1].split(',')]
im = np.transpose(np.array(temp_data).reshape((24,32)))
result = fil.gaussian_filter(im, 2)
plt.axis('scaled')
fig, (ax0, ax1) = plt.subplots(1, 2)
c = ax0.pcolor(im)
fig.colorbar(c, ax=ax0)
# plt.gca().set_aspect('equal', adjustable='box')
d = ax1.pcolor(result)
fig.colorbar(c, ax=ax1)
# plt.gca().set_aspect('equal', adjustable='box')
ax1.axis('equal')
ax0.axis('equal')

plt.show()