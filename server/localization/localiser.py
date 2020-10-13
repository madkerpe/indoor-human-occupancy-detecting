import cv2
import numpy as np
import json
from localization.processing import ImageProcessor
from help_module.time_helper import clean_diff, abs_diff, get_time_str
from PIL import Image, ImageDraw

class Localiser:
    def __init__(self, sensor_id):
        self.sensor_id=sensor_id
        self.matrix=None
        self.calibration_points=[] # key=px_index, val=world_coord
        self.tracker = None
        self.processcor = ImageProcessor()
        self.com_module = None
        # if this flag is true, all centroids are converted to world coords before
        # sending to the tracker
        self.WORLD_CORDS_FLAG = True
        self.calibrated = True
        self.timestamp = None

    def __add_calibration_point(self,cam_x,cam_y,world_x,world_y):
        self.calibration_points.append([[cam_x,cam_y],[world_x,world_y]])

    def __add_calibration_array(self,left_x,left_y,right_x,right_y,n):
        for i in range(n):
            x_i=left_x+i/n*right_x
            y_i=left_y +i/n*right_y
            self.__add_calibration_point(self,x_i,y_i)

    def __determine_matrix(self):
        if not len(self.calibration_points)>=3:
            print("NOT ENOUGH POINTS")
            self.matrix = None
        else:
            self.calibration_points = np.array(self.calibration_points).astype(np.float32)
            self.matrix, h = cv2.findHomography(self.calibration_points[:, 0], self.calibration_points[:, 1],cv2.LMEDS)
        return self.matrix



    def __update_world_co(self, centroids):
        # each value in centroids should be a pair (loc, timestamp)
        self.tracker.update(centroids)

    def get_world_cords(self, points):
        # print("localiser for" + str(self.sensor_id))
        if self.matrix is None:
            print("not yet callibrated")
            return points
        else:
            world_cords = []
            for point in points:
                vec = np.array([point[0],point[1],1])
                cord = np.matmul(self.matrix,np.transpose(vec))
                cord *= 1/cord[2]
                world_cords.append(cord[0:2])
            return world_cords

    def calibrate_data(self):
        print("Calibrating data")
        with open(r'D:\Programmeer projecten\VOP\server\configuration_files\calibration_configuration.json', 'r') as f:
            print("opened file")
            config = json.load(f)
            data=config['calibration_data']
            print(data)
            for key,value in data.items():
                debug = value.get(str(self.sensor_id),None)
                if value.get(str(self.sensor_id),None):
                    debug = min(value.get(str(self.sensor_id)))
                    if min(value.get(str(self.sensor_id)))>0:
                        #if <0 this point is not seen by the sensor
                        img_cord=value.get(str(self.sensor_id))
                        world_cord=config["points"][key]
                        self.__add_calibration_point(img_cord[0],img_cord[1],world_cord[0],world_cord[1])
                        print('calibration points added for '+str(self.sensor_id))
        self.__determine_matrix()
        self.calibrated = True
        print(self.calibration_points)

    def set_tracker(self, tracker):
        self.tracker = tracker

    def set_com_module(self, com_module):
        self.com_module = com_module

    def update(self, data, timestamp):
        self.timestamp = timestamp
        self.processor.set_thermal_data(data)
        if self.com_module is not None and self.com_module.any_clients():
            imgs = self.processor.get_imgs()
            self.com_module.distribute_imgs(self.sensor_id, imgs)
        if not self.WORLD_CORDS_FLAG:
            # print('img cords update by localiser')
            self.tracker.update(self.processor.get_centroids(), timestamp)
        else:
            if self.calibrated:
                # print('world cord update by localiser')
                world_coords = self.get_world_cords(self.processor.get_centroids())
                self.tracker.update(world_coords, timestamp)
                if self.com_module is not None:
                    self.com_module.localiser_update({'co': world_coords, 'id': self.sensor_id})

    def get_scaled_img(self, des_size):
        img = self.processor.plot_centroids(rgb=True)
        img = img.repeat(2, axis=0)
        img = img.repeat(2, axis=1)

        img = Image.fromarray(img, 'RGB')

        img_width = img.size[0]
        img_height = img.size[1]
        comp = Image.new('RGB', (img_width, img_height + 20))
        comp.paste(img, (0, 20))
        local_time = get_time_str(self.timestamp, microseconds=True, seconds=True)
        d = ImageDraw.Draw(comp)
        d.text((0, 0), local_time, fill=(255, 255, 255))
        comp.thumbnail(des_size, Image.ANTIALIAS)
        return comp


if __name__=='__main__':
    loc=Localiser(70)
    loc.calibrate_data()
    print(loc.get_world_cords([[108,203]]))
    print(loc.calibrated)


