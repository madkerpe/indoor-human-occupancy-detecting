import cv2
import numpy as np
import scipy.ndimage.filters as filter
import math
from help_module.img_helper import fast_thermal_image, get_deltas_img, get_thermal_color_tuples, color_from_indices
import logging
from PIL import Image


class ImageProcessor:
    def __init__(self):
        self.dim = (24, 32)

        self.thermal_data = None
        self.scale_factor = 10

        # These variables need to be reset when new thermal data is added
        self.scaled_data = None
        self.smooth_data = None
        self.thresh_data = None
        self.deltas = None
        self.centroids = None
        self.contours = None
        self.contour_hier = None

        self.thresh_method = self._set_bin_thresh
        self.erode = 0

        self.sensor_id = None

        self.scale_imgs = 1

        self.log_system = logging.getLogger('ImageProcessingLogger')
        self.enable_checkerboard = True

        self.checkerboard = np.array([[0,1] * 16, [1, 0] * 16] * 12)
        a = 5

    class decorators:
        """
        This class is used to add decorators to the functions of the ImageProcessor class, these decorators
        are used to check if the needed variables are valid and if they are not generate that data.
        The check_thermal data throws an exception if no thermal data is present.
        """
        @staticmethod
        def check_scaled_data(func):
            def wrapper(self, *args, **kwargs):
                self.log_system.info('check_scaled_data')
                if self.scaled_data is None:
                    self._set_scaled_data()
                return func(self, *args, **kwargs)

            return wrapper

        @staticmethod
        def check_smooth_data(func):
            def wrapper(self, *args, **kwargs):
                self.log_system.info('check_smooth_data')
                if self.smooth_data is None:
                    self._set_smooth_data()
                return func(self, *args, **kwargs)

            return wrapper

        @staticmethod
        def check_tresh_data(func):
            def wrapper(self, *args, **kwargs):
                self.log_system.info('check_thresh_data')
                if self.thresh_data is None:
                    self.thresh_method()
                return func(self, *args, **kwargs)

            return wrapper

        @staticmethod
        def check_centroids(func):
            def wrapper(self, *args, **kwargs):
                self.log_system.info('check_centroids')
                if self.centroids is None:
                    self._set_centroids()
                return func(self, *args, **kwargs)

            return wrapper

        @staticmethod
        def check_deltas(func):
            def wrapper(self, *args, **kwargs):
                self.log_system.info('check_deltas_data')
                if self.deltas is None:
                    self._set_deltas()
                return func(self, *args, **kwargs)

            return wrapper

        @staticmethod
        def check_thermal_data(func):
            def wrapper(self, *args, **kwargs):
                self.log_system.info('check_thermal_data')
                if self.thermal_data is None:
                    raise Exception('Processing: thermal_data not set')
                return func(self, *args, **kwargs)

            return wrapper

        @staticmethod
        def allow_rgb_switch(func):
            def wrapper(self, rgb=False):
                img = func(self)
                if rgb:
                    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

                return img

            return wrapper

    def enable_logging(self):
        """
        If you want output in the terminal, use this function.
        :return:
        """
        c_handler = logging.StreamHandler()
        self.log_system.addHandler(c_handler)
        self.log_system.setLevel(logging.INFO)

    def set_thermal_data(self, thermal_data):
        """
        This function is the function to input data into the class. The useful output only gets calculated
        when needed.
        :param thermal_data: numpy array with dim 786
        :return:
        """
        self.log_system.info('setting thermal data')
        self.thermal_data = thermal_data
        self._reset()

    @decorators.check_centroids
    def get_centroids(self):
        """
        Get the location of the hotspots on the thermal data.
        :return:
        """
        return self.centroids

    @decorators.check_centroids
    def get_calib_points(self):
        max_temp = 0
        max_co = (-1, -1)
        for centroid in self.centroids:
            if self.smooth_data[centroid[1], centroid[0]] > max_temp:
                max_temp = self.smooth_data[centroid[1], centroid[0]]
                max_co = centroid

        return max_co

    def get_imgs(self):
        """
        This function save all the steps in the processing process as images.
        TODO: complete with additional steps
        :return:
        """
        img1 = self.get_scaled_img()
        img2 = self._get_smooth_img()
        img3 = self._get_thresh_img()
        img4 = self._get_all_centroid_img()
        img5 = self._get_centroid_img()

        return [img1, img2, img3, img4, img5]

    def process(self, thermal_data):
        self.set_thermal_data(thermal_data)
        return self.get_centroids()


    @decorators.allow_rgb_switch
    @decorators.check_centroids
    def plot_centroids(self, rel_pos=False):
        '''
        Function that plots the centroids on a representation of the thermal data (fast_thermal_img)
        :param rel_pos: determines whether the relative coords are added to the figure
        :return: np array in RGB format
        '''
        # add centroids
        draw_img = cv2.cvtColor(self._get_thresh_img(as_numpy=True, scale=1), cv2.COLOR_RGB2BGR)

        for centroid in self.centroids:
            [cX, cY] = centroid
            cv2.circle(draw_img, (cX, cY), 1, (255, 255, 255), -1)
            if rel_pos:
                string = str(cX) + "," + str(cY)
                if cX > self.scale_factor * 32 / 2:
                    pos_x = min(cX - len(string) * 10, 32 * self.scale_factor - 15 * (len(string)))
                else:
                    pos_x = cX + 20
                if cY > self.scale_factor * 24 / 2:
                    pos_y = cY - 10
                else:
                    pos_y = cY + 30
                cv2.putText(draw_img, string, (pos_x, pos_y), cv2.QT_FONT_NORMAL, 0.4, (255, 255, 255))
        # add contours
        result = cv2.drawContours(draw_img, self.contours, -1, (0,0,255), thickness=1)  # params: all contours,color,thickness
        return result

    @decorators.allow_rgb_switch
    @decorators.check_centroids
    def plot_all_contours(self):
        draw_img = cv2.cvtColor(self._get_thresh_img(as_numpy=True, scale=1), cv2.COLOR_RGB2BGR)

        # add contours
        for contours in self.contour_hier:
            draw_img = cv2.drawContours(draw_img, contours, -1, (0, 0, 255), thickness=1)

        return draw_img

    @decorators.allow_rgb_switch
    @decorators.check_centroids
    def plot_contour_progression(self):
        mod_thresh = self.thresh_data.copy()
        unique_val = np.unique(mod_thresh)
        img_array = []

        # Add biggest contours
        or_contours, hierarchy = cv2.findContours(mod_thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        prev_contours = [or_contours]
        draw_img = self._get_thresh_img(as_numpy=True, scale=1, numpy_img=mod_thresh)
        draw_img = cv2.drawContours(draw_img, or_contours, -1, (255,0,0), thickness=2)
        img_array.append(Image.fromarray(draw_img, 'RGB'))

        # Add contours within other contours
        for i in range(1, unique_val.size - 1):
            mod_thresh[mod_thresh == unique_val[i]] = 0
            con, _ = cv2.findContours(mod_thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            draw_img = self._get_thresh_img(as_numpy=True, scale=1, numpy_img=mod_thresh)
            draw_img = cv2.drawContours(draw_img, con, -1, (255, 0, 0), thickness=2)

            for prev_con in prev_contours:
                draw_img = cv2.drawContours(draw_img, prev_con, -1, (255, 255, 255), thickness=1)

            prev_contours.append(con)
            img_array.append(Image.fromarray(draw_img, 'RGB'))

        return img_array


    def _reset(self):
        """
        Sets all the needed variables to None in order to show that new thermal data is added and the
        old values are invalid.
        :return:
        """
        self.log_system.info('resetting')

        self.contours = None
        self.centroids = None
        self.thresh_data = None
        self.scaled_data = None
        self.smooth_data = None
        self.deltas = None

    @decorators.check_thermal_data
    def _set_scaled_data(self):
        ######CUT AWAY THE EDGES#################
        # full_image = np.reshape(self.thermal_data, (24, 32))
        # self.scaled_data =  full_image[4:20,8:24]
        #####CUT AWAY THE EDGES#################
        self.scaled_data = np.reshape(self.thermal_data, (24, 32)) * self.checkerboard
        # self.scaled_data = np.reshape(self.thermal_data, (24, 32))
        self.scaled_data = self.scaled_data.repeat(10, axis=0)
        self.scaled_data = self.scaled_data.repeat(10, axis=1)

    @decorators.check_scaled_data
    def _set_smooth_data(self):
        """
        Creates an image (numpy array is good for opencv) that is needed for further analyzing the image,
        First the image gets scaled because opencv works better when there is a bit more resolution.
        Then a blur is added to smooth out the noise. The numpy array has to be np.uint8 to be valid for opencv.
        :return:
        """
        self.log_system.info("Setting image")

        self.smooth_data = filter.gaussian_filter(self.scaled_data, 15).astype(np.uint8)

    @decorators.check_smooth_data
    def _set_deltas(self):
        """
        This funtion is used to set the deltas for the fast_thermal_image functions, these deltas are needed to
        make the colors equal on the different images.
        :return:
        """
        self.deltas = get_deltas_img(self.smooth_data)

    @decorators.check_smooth_data
    def _set_thresh_data(self):
        """
        This function is used to remove the background from the image, this is done by removing everything
        smaller and equal then the temperature that is used most in the image (histogram max).
        :return:
        """

        self.log_system.info("Setting thresh img")

        hist_amount, hist_temp = np.histogram(self.smooth_data, bins=20)

        peaks = []

        for i in range(1, len(hist_amount) - 1):
            prev = hist_amount[i - 1]
            cur = hist_amount[i] * 1.2
            next = hist_amount[i + 1]
            if prev < cur and next < cur:
                peaks.append(hist_temp[i])
        thresh = self.smooth_data.copy()

        thresh[thresh <= math.ceil(peaks[2])] = 0
        thresh = cv2.erode(thresh, None, iterations=self.erode)
        self.thresh_data = thresh

    @decorators.check_deltas
    @decorators.check_smooth_data
    def _set_bin_thresh(self):
        diff = np.max(self.thermal_data) - np.min(self.thermal_data)

        print(f'diff is {diff}')
        if diff <= 20:
            self.thresh_data = np.zeros(self.smooth_data.shape).astype(np.uint8)
        else:
            self.thresh_data = np.zeros(self.smooth_data.shape).astype(np.uint8)
            for value_range, value in zip(reversed(self.deltas), reversed(range(len(self.deltas)))):
                self.thresh_data[self.smooth_data <= value_range] = value

            self.thresh_data[self.thresh_data <= 5] = 0

            self.thresh_data = cv2.erode(self.thresh_data, None, iterations=2)

    @decorators.check_tresh_data
    def _set_centroids(self):
        """
        This function calculates the centroids from the thresh image. The thresh_img should be set for the initial
        contours. This function also tries to improve the initial contours be searching smaller contours within the
        bigger contours.
        :return:
        """
        print("setting centroids")
        self.log_system.info("Setting centroids")

        self.centroids = []

        unique_val = np.unique(self.thresh_data)

        # Add biggest contours
        or_contours, hierarchy = cv2.findContours(self.thresh_data, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        self.contour_hier = [or_contours]
        mod_thresh = self.thresh_data.copy()

        # Add contours within other contours
        for i in range(1, unique_val.size - 1):
            mod_thresh[mod_thresh == unique_val[i]] = 0
            con, _ = cv2.findContours(mod_thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            new_contours = []
            for contour in con:
                if cv2.contourArea(contour) > 200:
                    new_contours.append(contour)

            self.contour_hier.append(con)

        self.contours = []
        self.contours.extend(self.contour_hier[-1])

        # Remove all contours that surround other contours
        for i in reversed(range(0, len(self.contour_hier) - 1)):
            for new_contour in self.contour_hier[i]:
                add_contour = True
                for current_contour in self.contours:
                    dst = cv2.pointPolygonTest(new_contour, (current_contour[0, 0, 0], current_contour[0, 0, 1]), True)
                    if dst >= 0:
                        add_contour = False

                if add_contour:
                    self.contours.append(new_contour)

        # Calculate x, y coordinate of contour center
        for c in self.contours:
            M = cv2.moments(c)

            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
            else:
                cX, cY = 0, 0

            self.centroids.append([cX, cY])
        self.centroids = self.remove_corners(self.centroids)
        print(self.centroids)

    def get_scaled(self, img, scale):
        new_img = img.copy()
        new_img = new_img.repeat(scale, axis=0)
        new_img = new_img.repeat(scale, axis=1)
        return new_img

    # @decorators.allow_rgb_switch
    @decorators.check_scaled_data
    @decorators.check_deltas
    def get_scaled_img(self):
        img = self.get_scaled(self.scaled_data, self.scale_imgs)
        return fast_thermal_image(img, dim=img.shape)

    @decorators.allow_rgb_switch
    @decorators.check_smooth_data
    @decorators.check_deltas
    def _get_smooth_img(self):
        img = self.get_scaled(self.smooth_data, self.scale_imgs)
        return fast_thermal_image(img, deltas=self.deltas, dim=img.shape)

    @decorators.check_tresh_data
    @decorators.check_deltas
    def _get_thresh_img(self, as_numpy=False, scale=1, numpy_img=None):
        if numpy_img is None:
            numpy_img = self.thresh_data
        colors = get_thermal_color_tuples()
        new_rgb = np.zeros((numpy_img.shape[0], numpy_img.shape[1], 3)).astype(np.uint8)
        for i in range(len(colors)):
            new_rgb[numpy_img == i] = np.array(colors[i])

        img = self.get_scaled(new_rgb, scale)

        if not as_numpy:
            return Image.fromarray(img, 'RGB')
        else:
            return img

    def _get_centroid_img(self):
        plot_img = self.plot_centroids(rgb=True)
        img = self.get_scaled(plot_img, self.scale_imgs)
        return Image.fromarray(img, 'RGB')

    def _get_all_centroid_img(self):
        plot_img = self.plot_all_contours(rgb=True)
        img = self.get_scaled(plot_img, self.scale_imgs)
        return Image.fromarray(img, 'RGB')

    @decorators.check_centroids
    @decorators.check_tresh_data
    def get_img_layers(self):
        img_arrays = []
        mod_thresh = self.thresh_data.copy()
        unique_val = np.unique(mod_thresh)

        # Add biggest contours
        or_contours, _ = cv2.findContours(mod_thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        new_img = color_from_indices(mod_thresh)
        new_img = cv2.drawContours(new_img, or_contours, -1, (0, 0, 255), thickness=1)
        img_arrays.append(new_img)

        # Add contours within other contours
        for i in range(1, unique_val.size - 1):
            mod_thresh[mod_thresh == unique_val[i]] = 0
            con, _ = cv2.findContours(mod_thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            new_contours = []
            for contour in con:
                if cv2.contourArea(contour) > 200:
                    new_contours.append(contour)

            new_img = color_from_indices(mod_thresh)
            new_img = cv2.drawContours(new_img, new_contours, -1, (0, 0, 255), thickness=1)
            img_arrays.append(new_img)

        imgs = []
        for img_ar in img_arrays:
            imgs.append(Image.fromarray(cv2.cvtColor(img_ar, cv2.COLOR_RGB2BGR), 'RGB'))

        return imgs

    def remove_corners(self, centroid_list):
        new_centroids = []
        for centroid in centroid_list:
            if 10 <= centroid[0] <= 310 and 10 <= centroid[1] <= 230:
                new_centroids.append(centroid)

        return new_centroids

