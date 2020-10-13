'''
this document contains help functions to process the np array from the DB
into a number of objects which are visualised and of which the centroid is determined
to use this class, all you need is the process function, see below
'''
import cv2
import numpy as np
import matplotlib.image as image
import scipy.ndimage.filters as filter


class ImageProcessor:
    def __init__(self):
        self.data=None
        self.dim=(24,32)
        self.img=None #BGR
        self.gray=None #range(255)
        self.thresh=None #[0|255]
        self.thresh_method="hist_cap"
        self.erode=10
        self.scale_factor=10
        self.thresh_methods=["otsu","hist_cap"]

        self.centroids=[] #2D array
        self.contours=[]

    def __get_img(self):
       self.data = np.reshape(self.data,self.dim).astype(np.uint8)
       self.data = filter.gaussian_filter(self.data, 1).astype(np.uint8)
       image.imsave('temp_img.png', self.data)
       self.img = cv2.imread('temp_img.png')
       self.__resize_img()

    def __resize_img(self):
        self.img = cv2.resize(self.img,None,fx=self.scale_factor,fy=self.scale_factor)

    def __process_into_binary(self):
        #TODO: filter empty frames
        self.gray=cv2.cvtColor(self.img,cv2.COLOR_BGR2GRAY)
        if self.thresh_method is "otsu":
            self.gray=255-self.gray
            ret, self.thresh = cv2.threshold(self.gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            self.thresh=255-self.thresh
            self.thresh = cv2.erode(self.thresh, None, iterations=self.erode)

        elif self.thresh_method is "hist_cap":
            hist = np.histogram(self.gray, 50)
            thresh_val = hist[1][-15] # -5 is random chosen #TODO make dynamic?
            ret, self.thresh = cv2.threshold(self.gray, thresh_val, 255, cv2.THRESH_BINARY)
        else:
            raise NotImplementedError

    def __determine_contours_centroids(self):
        #clear old centroids
        self.centroids=[]
        self.contours, hierarchy = cv2.findContours(self.thresh.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # print('num of contours=' + str(len(self.contours)))
        for c in self.contours:
            ##print(cv2.contourArea(c))
            #TODO:area filtering
            # calculate moments for each contour
            M = cv2.moments(c)
            # calculate x,y coordinate of center
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
            else:
                cX, cY = 0, 0
            # print(f'found centroid: {cX}, {cY}')
            self.centroids.append([cX,cY])

    def process(self,data):
        '''
        this is the public function which implements the whole process
        :param data: a np array of size 24*32 (dimensions don't matter), containing RAW sensor_data
        :return:
        '''
        assert (np.size(data)==int(self.dim[0]*self.dim[1]))
        self.data=data
        self.__get_img()
        self.__process_into_binary()
        self.__determine_contours_centroids()


    def set_treshold_method(self,method):
        '''
        public function to change threshold method
        :param method: a string, element of self.thresh_methods
        :return:
        '''
        assert (method in self.thresh_methods)
        self.thresh_method = method

    def plot_frame(self,rel_pos=True):
        '''
        public function which adds current centroids & contours to the current image
        :param rel_pos: determines whether the relative coords are added to the figure
        :return: np array in RGB format
        '''
        #add centroids
        for centroid in self.centroids:
            [cX,cY]=centroid
            cv2.circle(self.img, (cX, cY), 5, (255, 255, 0), -1)
            if (rel_pos):
                string=str(cX)+","+str(cY)
                if cX>self.scale_factor*32/2:
                    pos_x=min(cX-len(string)*10,32*self.scale_factor-15*(len(string)))
                else:
                    pos_x=cX+20
                if cY>self.scale_factor*24/2:
                    pos_y=cY-10
                else:
                    pos_y=cY+30
                cv2.putText(self.img,string,(pos_x,pos_y),cv2.QT_FONT_NORMAL,0.8,(255,255,255))
        #add contours
        cv2.drawContours(self.img, self.contours, -1, 100, 3) #params: all contours,color,thickness
        return cv2.cvtColor(self.img.copy(),cv2.COLOR_BGR2RGB)
