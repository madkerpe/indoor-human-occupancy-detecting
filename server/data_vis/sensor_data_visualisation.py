#query used to obtain the csv 21-02
'''
select data, timestamp ,"sequence_ID", "sensor_ID"
from public."Sensor_data"
where "sensor_ID"=51
order by timestamp, "sequence_ID"
'''

'''
this file is used to plot histograms of an episode
'''

import csv
import numpy as np
import matplotlib.pyplot as plt
from help_module.csv_helper import read_data
import scipy.ndimage.filters as filter



data=read_data('files/sensor_data_episode_20190221-143435_0.csv',0,502) #manually selected empty frames of this episode

for i in range(100,110):
    plt.figure()
    im = data[i][0].reshape((24, 32))
    im_b = filter.gaussian_filter(im, 1).astype(np.uint8)
    plt.hist(im_b,50)
plt.show()


