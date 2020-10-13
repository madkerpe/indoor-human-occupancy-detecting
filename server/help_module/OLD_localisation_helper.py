from help_module.img_processing_helper import ImageProcessor
import numpy as np
import math
'''
for this class, the assumption is made that the sensor is positioned in a plane,
parallel to the plane which contains the floor
'''
class Localiser (ImageProcessor):
    def __init__(self):
        ImageProcessor.__init__(self)
        self.data_height=180
        self.sensor_height=0
        self.sensor_center=(0,0)
        self.origin_corner=(0,0) #corner for which centroid would be (0,0)
        #from documentation, in top view this is the right upper corner with respect to the notch

        self.absolute_positions=[]
        self.rotmatrix=np.matrix(np.zeros((2,2)))
        self.transmatrix=np.matrix(np.zeros((2,1)))
        self.pixels=(self.scale_factor*32,self.scale_factor*24)
        self.x_pixel_length=0
        self.y_pixel_length=0

    def __determine_transformation_matrix(self):
        # determine angle between system of the room and relative system
        angle= math.atan((self.center[1]-self.origin_corner[1])/(self.center[0]-self.origin_corner[0]))-math.atan(12/16)
        print("angle="+str(angle*180/math.pi))
        c,s=math.cos(angle),math.sin(angle)
        #X= ROT.x + T to go from pixel index to absolute position
        self.rotmatrix=np.matrix([[c,-s],[s,c]])
        self.transmatrix=np.matrix([[c,-s],[s,c]])*np.matrix([[-self.x_pixel_length*self.scale_factor*16],[-12*self.scale_factor*self.y_pixel_length]])
        self.transmatrix+=np.matrix([[self.center[0]],[self.center[1]]])
        print('rot='+str(self.rotmatrix))
        print('trans='+str(self.transmatrix))
    def set_corner_and_center(self,corner,center):
        '''
        set the absolute positioning of the sensor
        :param corner: in centimeter! choose correct corner (closest to the room coordinate system origin (right upper from notch
        :param center: in centimeter!
        :return:
        '''
        assert(self.sensor_height>0)
        self.center=center
        if corner[0]<center[0] and corner[1]<center[1]: #origin corner under assumption of small angle!
            self.origin_corner=corner
        else:
            raise NotImplementedError
        self.__determine_transformation_matrix()


    def set_heigt(self,height):
        '''
        set height and check accuracy of measurements
        :param height: height in CM of sensor to the floor
        :return: sqaure of the difference between the two calculation methods
        '''
        self.sensor_height=height
        self.x_pixel_length=math.sin(55/180*math.pi)*(self.sensor_height-self.data_height)/(16*self.scale_factor)
        self.y_pixel_length=math.sin(35/180*math.pi)*(self.sensor_height-self.data_height)/(12*self.scale_factor)

    def get_error(self):
        dst = math.sqrt((self.sensor_center[0] - self.origin_corner[0]) ** 2 + (self.sensor_center[1] - self.origin_corner[1]) ** 2)
        print(dst)
        x = math.sin(55 / 180 * math.pi) * (self.sensor_height - self.data_height)  # subtract human body length from ceiling height
        y = math.sin(35 / 180 * math.pi) * (self.sensor_height - self.data_height)
        calc_dst = math.sqrt(x ** 2 + y ** 2)
        print(calc_dst)
        err = dst - calc_dst
        return err

    def get_abs_locations(self):
        '''
        requires both height and center to be set!
        essential function of this class: calculates absolute position of the blobs in the current frame
        :return: returns an array of absolute locations
        '''
        assert(self.sensor_height>0)
        assert(self.center[0]>0)

        centroids=np.array(self.centroids.copy())
        self.absolute_positions=[]
        for centroid in centroids:
            #scale pixel index to absolute position
            centroid[0]*=self.x_pixel_length
            centroid[1]*=self.y_pixel_length
            #transformation
            centroid=self.rotmatrix*centroid.reshape((2,1))+self.transmatrix
            #some reshaping
            centroid=np.array(centroid).astype(np.uint16).reshape((1,2))
            self.absolute_positions.append([centroid[0][0],centroid[0][1]])
        return self.absolute_positions











