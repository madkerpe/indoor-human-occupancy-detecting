from filterpy.kalman import KalmanFilter
from filterpy.common import Q_discrete_white_noise
from scipy.linalg import block_diag
import numpy as np
from functools import lru_cache
import datetime

class AdaptedKalmanFilter(KalmanFilter):

    # We kunnen witte ruis in rekening brengen, we kunnen gokken dat de omzetting naar wereldcoordinaten een halve meter misrekent
    #Q_STD = 200

    '''
    This class Extends the Kalman to allow for irregular time intervals
    '''
    def __init__(self,position, timestamp,dim_x = 4,dim_z = 2):
        '''
        constructor
        :param dim_x: number of state variables
        :param dim_z: number of measurment variables
        :param position: current 2D position and velocity
        :param timestamp: current timestamp
        '''


        super().__init__(dim_x,dim_z)
        self.x = np.asarray([position[0], 1, position[1], 1])
        #De gemiddelde snelheid van een wandelaar is 1.38 m/s, dus pak geprojecteerd op de assen 0.98 m/s
        #We ronden af naar één

        self.previous_timestamp = timestamp
        self.time_difference = 0

        self.H = np.array([[1, 0, 0, 0], [0, 0, 1, 0]])

        #De std van een wandelaar is 0.37m^2, de variantie op locatie is een gok
        self.P = np.diag([100, 3500, 100, 3500])
        
        #We kunnen witte ruis in rekening brengen, maar dit lijkt mij overbodig
        #q = Q_discrete_white_noise(dim=2, dt=0, var=AdaptedKalmanFilter.Q_STD**2)
       # self.Q = block_diag(q, q)

        #TODO: F should use time_difference to update x using dx/dt
        self.B = np.zeros(1) #no controller actions
        self.u = np.zeros((1)) #no controller actions
        self.F = np.eye(dim_x) # velocity is updated in update_time_diff

        self.R = np.diag([1,1])*500
        self.Q *= 500
        #Ik heb geen idee van hoe we R kunnen initialiseren


    def predict(self,timestamp):
        self.__update_timedifference(timestamp)
        super().predict()

    @lru_cache()
    def get_prediction(self,timestamp):
        '''
        this function performs a prediction without actually changing the internal state
        this allows to do multiple predictions (for different timestamps) before deciding
        which timestamp is definitive one and update the state
        :param timestamp: timestamp of the prediction you want
        :return: (x,P) with x the internal state and P the covariance matrix
        '''
        self.__update_timedifference(timestamp)
        return super().get_prediction()

    def update(self,z, timestamp):
        '''
        updates just like normal Kalman but sets time difference first and sets previous
        timestamp after update
        :param z: measurement
        :param timestamp: timestamp of the measurement
        :return:
        '''
        self.__update_timedifference(timestamp)
        super().update(z)
        self.previous_timestamp = timestamp #update internal timestamp
        self.time_difference = 0

    def batch_filter(self, zs, ts):
        '''
        allows to give the filter an array of measurements and get results
        :param zs: array of measurements
        :param ts: array of timestamps (same dim)
        :return:  (means, P, means_predict, P_predict)
        '''
        assert(len(ts) == len(zs))

        fs = []
        for time in ts: #create array of F matrices
            self.__update_timedifference(time)
            fs.append(self.F)
        return super().batch_filter(zs,fs)

    def __update_timedifference(self,timestamp):
        '''

        :param timestamp: time in seconds
        :return:
        '''
        self.time_difference = timestamp - self.previous_timestamp
        self.F[0, 1] = self.time_difference
        self.F[2, 3] = self.time_difference
        
        #We kunnen witte ruis in rekening brengen, maar dit lijkt mij overbodig
        #q = Q_discrete_white_noise(dim=2, dt=self.time_difference, var=AdaptedKalmanFilter.Q_STD**2)
        #self.Q = block_diag(q, q)

    def get_location(self):
        mask = np.array([True,False,True,False])
        return self.x[mask]

if __name__ == "__main__":
    KF = AdaptedKalmanFilter(np.array([0.,0]),0)
    print(KF.get_location())
    print(KF.get_prediction(12))
    KF.predict(12)
    print(KF.x)
    KF.update(np.array([10.,17]),12)
    print(KF.x)
    KF.predict(24)
    print(KF.x)
    KF.update(np.array([10., 17]), 24) #simulate stopping
    print(KF.x)
