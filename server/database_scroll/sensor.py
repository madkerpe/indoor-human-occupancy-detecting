from PyQt5.QtWidgets import QGraphicsScene, QFileDialog, QCheckBox, QLabel, QHBoxLayout
from help_module.csv_helper import load_csv
from help_module.data_model_helper import Measurement_db, Base, CSV_Measurement, Measurement
from help_module.img_helper import fast_thermal_image, plt_fig_to_PIL, get_deltas_img, grid_plot, hist_plot
from help_module.time_helper import abs_diff
from localization.processing import ImageProcessor
from datetime import timedelta
import scipy.ndimage.filters as filter
from matplotlib.figure import Figure
import numpy as np
import cv2
from PIL import Image

class Sensor:
    def __init__(self, db_bridge, app):
        self.db_bridge = db_bridge
        self.app = app

        self.layout = None
        self.label = None
        self.checkbox = None

        self.checkbox_callback = None
        self.img_processor = ImageProcessor()

        self.start_time = None
        self.stop_time = None

        self.meas_list = None

    def set_sensor_values(self, sensor_type, sensor_id=None, file_name=None, data=None):
        self.sensor_type = sensor_type
        self.meas_list = data
        self.file_name = file_name
        self.sensor_id = sensor_id

    def checkbox_activate(self):
        self.checkbox_callback(self)

    def create_ui(self, callback):
        self.layout = QHBoxLayout()
        self.label = QLabel(f'{self.sensor_type}: {self.sensor_id if self.sensor_id is not None else self.file_name}')
        self.checkbox = QCheckBox()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.checkbox)

        self.checkbox_callback = callback
        self.checkbox.stateChanged.connect(self.checkbox_activate)

        return self.layout

    def delete_ui(self):
        self.layout.deleteLater()
        self.label.deleteLater()
        self.checkbox.deleteLater()

    def data_loaded(self):
        return self.meas_list is not None

    def reload(self):
        if self.meas_list is not None:
            self.load_data()

    def is_active(self):
        return self.checkbox.isChecked()

    def get_data(self):
        if self.meas_list is None:
            print("WARNING attempting to load data that is not loaded")
        return self.meas_list

    def load_data(self):
        """
        This function takes a source and then looks at its type to find the function to get that data

        :param source: A dict containing all the information to load the data
        :return: list of measurements
        """
        if self.sensor_type == 'csv':
            self.meas_list = load_csv(self.file_name)
        elif self.sensor_type == 'sensor':
            self.meas_list = self.load_sensor()
        else:
            raise Exception('Source type was not recognized')

        self.start_time = self.meas_list[0].timestamp
        self.stop_time = self.meas_list[-1].timestamp

        for index, meas in enumerate(self.meas_list):
            meas.set_or_index(index)
            meas.set_sensor(self)
            meas.convert_to_numpy()


    def load_sensor(self):
        """
        Uses a database query to get measurements from the sensor with id == sensor_id
        Explanation for converting to different class is written in the data_model_helper.py

        :param sensor_id:
        :return:
        """
        param = self.app.get_query_param()
        db_values = self.db_bridge.get_values(self.sensor_id, param)
        sens_values = [Measurement(meas) for meas in db_values]

        return sens_values

    def get_default_vis(self, index):
        thermal_data = self.meas_list[index].data
        self.img_processor.set_thermal_data(thermal_data)
        imgs_batch_1 = self.img_processor.get_imgs()

        print(f'diff in thermal_data: {np.max(thermal_data) - np.min(thermal_data)}')

        return imgs_batch_1

    def get_multi_processing(self, index):
        hist_amount = self.img_processor.get_hist_length()
        start_index = max(0, index - hist_amount)
        prev_frames = [meas.data for meas in self.meas_list[start_index:index]]
        cur_frame = self.meas_list[index].data

        self.img_processor.set_current_frame(cur_frame)
        self.img_processor.set_history(prev_frames)

        return self.img_processor.subtract_history()

    def get_closest_meas(self, time):
        cur_time = timedelta(seconds=time)

        min_diff = float('inf')
        min_index = 0

        for meas, index in enumerate(self.meas_list):
            if abs_diff(meas.timestamp, cur_time) < min_diff:
                min_diff = abs_diff(meas.timestamp, cur_time)
                min_index = index

        return min_index
