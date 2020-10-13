import serial
import numpy as np
import matplotlib.pyplot as plt
import scipy.ndimage.filters as fil
ser = serial.Serial()
ser.baudrate = 115200
ser.port = 'COM8'
ser.open()
while True:
    res = np.array(str(ser.readline()).replace("'", ",").split(",")[1:-2])

    print(res)
    print(len(res))
    if len(res) == 768:
        res = [float(a) for a in res]
        res = np.reshape(res,(24,32))
        res = fil.gaussian_filter(res, 1)
        plt.pcolor(res)
        plt.colorbar()
        plt.show()

