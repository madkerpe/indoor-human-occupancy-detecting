import sys
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon, QPixmap, QImage, QTransform
import scipy.ndimage.filters as fil
from PyQt5.QtWidgets import QGraphicsScene, QFileDialog, QCheckBox, QLabel, QHBoxLayout
from PyQt5.QtCore import QDateTime, QSize

import numpy as np
import json
import operator
import time
from PIL.ImageQt import ImageQt
import math
from datetime import timedelta


from server.database_scroll.ui_generated import Ui_MainWindow
from help_module.data_model_helper import Measurement_db, Base, CSV_Measurement
from help_module.time_helper import meas_to_time, clean_diff, get_time_str
from help_module.csv_helper import load_csv, write_csv_list_frames, write_csv_frame
from help_module.img_helper import get_grid_form


from server.database_scroll.qt_extra_classes import ZoomQGraphicsView
from server.database_scroll.db_bridge import DB_Bridge
from server.database_scroll.sensor import Sensor
import logging


class MyUI(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.episode_index = -1
        self.frame_index = 0
        self.frame_jump = 10
        self.max_time = 0
        self.download_path = ''
        self.sensor = 0
        self.episode_selected = False

        self.episodes = []
        self.episode_sensors = []

        self.update_from_button = False

        self.ui.refreshButton.clicked.connect(self.reload_db)
        self.ui.timeList.currentRowChanged.connect(self.episode_clicked)

        self.ui.forwardOneButton.clicked.connect(self.one_forward)
        self.ui.backwardOneButton.clicked.connect(self.one_backward)
        self.ui.forwardMoreButton.clicked.connect(self.more_forward)
        self.ui.backwardMoreButton.clicked.connect(self.more_backward)

        self.ui.connectTimeSpinbox.valueChanged.connect(self.update_connect_time)
        self.ui.sliceTimeSpinbox.valueChanged.connect(self.update_slice_time)

        self.ui.timeSlider.valueChanged.connect(self.move_timeslider)

        self.ui.saveCSVFRAMEButton.clicked.connect(self.write_csv_current_frame)
        self.ui.saveCSVEPISODEButton.clicked.connect(self.write_csv_current_episode)
        self.ui.loadCSVButton.clicked.connect(self.load_csv_button)

        now = QDateTime()
        now.setSecsSinceEpoch(time.time())

        yesterday = QDateTime()
        yesterday.setSecsSinceEpoch(time.time() - 24*60*60)

        self.ui.startTimeEdit.setDateTime(yesterday)
        self.ui.stopTimeEdit.setDateTime(now)

        self.connect_time = self.ui.connectTimeSpinbox.value()
        self.slice_time = self.ui.sliceTimeSpinbox.value()

        self.plotGraphicsView = ZoomQGraphicsView()

        self.ui.rightVLayout.insertWidget(0, self.plotGraphicsView)
        self.plot_scene = QGraphicsScene()
        self.plotGraphicsView.setScene(self.plot_scene)

        self.ui.frameAmountSpinbox.valueChanged.connect(self.update_episodes_ui_update)
        self.ui.sliceTimeSpinbox.valueChanged.connect(self.update_episodes_ui_update)
        self.ui.connectTimeSpinbox.valueChanged.connect(self.update_episodes_ui_update)
        self.ui.stopTimeEdit.dateTimeChanged.connect(self.update_episodes_ui_update)
        self.ui.startTimeEdit.dateTimeChanged.connect(self.update_episodes_ui_update)
        self.ui.ignoreStartCheckbox.stateChanged.connect(self.update_episodes_ui_update)
        self.ui.ignoreStopCheckbox.stateChanged.connect(self.update_episodes_ui_update)

        self.sensors = []

        self.or_index_counter = 0
        
        self.logger = logging.getLogger('database_scroll_logger')

        self.db_bridge = DB_Bridge()

    def update_connect_time(self, value):
        self.logger.info("update connect time to " + str(value))
        self.connect_time = value

    def update_slice_time(self, value):
        self.logger.info("update slice time to: " + str(value))
        self.slice_time = value

    def one_forward(self):
        self.move_time_or_frame(1)

    def one_backward(self):
        self.move_time_or_frame(-1)

    def more_forward(self):
        self.move_time_or_frame(self.frame_jump)

    def more_backward(self):
        self.move_time_or_frame(-self.frame_jump)

    def move_time_or_frame(self, frame_jump):
        if 0 <= self.frame_index + frame_jump < len(self.episodes[self.episode_index]):
            self.frame_index += frame_jump

        self.adjust_after_shift()

    def adjust_after_shift(self):
        self.logger.info("Adjust after shift")

        slider_index = self.frame_index

        self.update_from_button = True
        self.ui.timeSlider.setValue(slider_index)
        self.draw_plot()

    def update_episodes_ui_update(self):
        self.reload_sources('sensor')
        self.update_episodes()

    def move_timeslider(self, value):
        if self.update_from_button:
            self.update_from_button = False
            return

        self.frame_index = value
        self.draw_plot()

    def load_csv_button(self):
        """
        Activated from ui.loadCSVButton, opens a filedialog and add csv if filename is valid
        :return:
        """
        fname = QFileDialog.getOpenFileName(self, 'Open file', 'c:\\', "CSV files (*.csv)")
        if fname[0] != "":
            self.add_source('csv', file_name=fname[0])

    def add_source(self, sensor_type, sensor_id=None, file_name=None, data=None):
        """
        Creates a source but doesn't load in the data, if type == 'csv' file_name should be specified
        If type == 'sensor' sensor_id should be used

        :param sensor_type:
        :param sensor_id:
        :param file_name:
        :return:
        """
        n_sensor = Sensor(self.db_bridge, self)
        n_sensor.set_sensor_values(sensor_type, sensor_id, file_name, data)
        new_layout = n_sensor.create_ui(self.sensor_state_changed)
        self.sensors.append(n_sensor)
        self.ui.sourcesVLayout.addLayout(new_layout)

    def clear_sources(self, sensor_type):
        """
        Clears the UI elements and the list that contain references to sources

        :param type: type of source to be removed
        :return:
        """
        n_list = [sensor for sensor in self.sensors if sensor.sensor_type != sensor_type]
        del_list = [sensor for sensor in self.sensors if sensor.sensor_type == sensor_type]

        for sensor in del_list:
            sensor.delete_ui()

        self.sensors = n_list

    def get_query_param(self):
        """
        This functions creates a dict that is needed to get the correct information from the db.
        This is needed because there is no direct connection with the db only via the db_bridge.
        :return:
        """
        param = {}
        param['act_start'] = not self.ui.ignoreStartCheckbox.isChecked()
        param['act_stop'] = not self.ui.ignoreStopCheckbox.isChecked()
        param['time_start'] = self.ui.startTimeEdit.dateTime().toPyDateTime()
        param['time_stop'] = self.ui.stopTimeEdit.dateTime().toPyDateTime()
        param['amount_limit'] = self.ui.frameAmountSpinbox.value()

        return param

    def reload_sources(self, type):
        """
        This function iterates over all the sensor and then reloads them. This is mainly used when changing the query
        parameters or loading newly created data from the database
        :param type: The specific type to reload ex: csv, useful because csv's don't have to be reloaded
        :return:
        """
        for sensor in self.sensors:
            sensor.reload()

    def sensor_state_changed(self, sensor):
        """
        This function looks at the selected sources and then creates a episode list.
        A episode is defined as measurements that all satisfy the conditions.

        cond1: The next measurement should be within self.connect_time from the previous one. This is used
        to separate different bursts of measurements. If zero this is ignored.

        cond2: The difference in time between first and last measurement should be smaller then
        self.slice_time. This is used to avoid excessive long episodes. If zero this is ignored.

        :param index: This gives the index of the current sensor index
        :return: Fills up self.episodes
        """

        # Load data if not loaded
        if not sensor.data_loaded():
            sensor.load_data()

        self.update_episodes()

    def update_episodes(self):
        """
        This function combines all the data from the active sensors (not actual sensor, the class) and creates one long
        list from them. After creating this list the values get sorted so the values are in chronological order.
        After the sorting the list get spliced up into episodes.

        A episode is defined as measurements that all satisfy these conditions:

        -cond1: The next measurement should be within connect time from the previous one.
                This is used to separate different bursts of measurements. If zero this is ignored.

        -cond2: The difference in time between first and last measurement should be smaller then the slice time.
                This is used to avoid excessive long episodes. If zero this is ignored.

        :return: -
        """
        # Combine data from different sources and sort for easier plotting
        data = []
        for sensor in self.sensors:
            if sensor.is_active():
                data.extend(sensor.get_data())

        data = sorted(data, key=operator.attrgetter('timestamp'), reverse=True)

        # Clear UI and setup variables
        self.episodes = []
        self.episode_sensors = []
        self.ui.timeList.clear()

        if len(data) == 0:
            return

        episode_starttime = data[0].timestamp
        current_starttime = data[0].timestamp
        current_episode = []
        current_set = {data[0].sensor_id}

        # Slice the data up into episodes
        for value in data:
            if len(current_episode) == 0:
                episode_starttime = value.timestamp

            diff_connect = (current_starttime - value.timestamp).seconds
            diff_slice = (episode_starttime - value.timestamp).seconds
            if (diff_connect < self.connect_time or self.connect_time == 0) and (diff_slice < self.slice_time or self.slice_time == 0):
                current_episode.append(value)
                current_set.add(value.sensor_id)
            else:
                if len(current_episode) > 0:
                    self.episodes.append(current_episode[::-1])
                    self.episode_sensors.append(current_set)
                current_episode = []
                current_set = set()
            current_starttime = value.timestamp

        if len(current_episode) > 0:
            self.episodes.append(current_episode[::-1])
            self.episode_sensors.append(current_set)

        # Create string for UI list and populate that list
        for episode in self.episodes:
            date_str = get_time_str(episode[0].timestamp, time=False)
            start_time_str = get_time_str(episode[0].timestamp, date=False)
            stop_time_str = get_time_str(episode[-1].timestamp, date=False)

            episode_str = f'{date_str} {start_time_str}->{stop_time_str}'
            self.ui.timeList.addItem(episode_str)

    def episode_clicked(self, index):
        """
        Gets called when the user click on listwidget inside ui.timeList. This function should find the
        selected episode and reset all the values so the first frame of the episode is ready to be plotted.
        The function then calls the plot function.

        Important variables that are changed:  episode_index, frame_index

        :param index: episode clicked on self.timeList
        :return:
        """
        if index < 0:
            self.clear_frame()
            return

        self.episode_index = index
        episode = self.episodes[index]
        self.frame_index = 0
        diff = (episode[-1].timestamp - episode[0].timestamp)
        self.max_time = diff.seconds

        self.ui.frameAmountLabel.setText(f'frame: 1/{len(episode)}')
        self.ui.startEpisodeLabel.setText(f'Start: {meas_to_time(episode[0])}')
        self.ui.endEpisodeLabel.setText(f'Stop: {meas_to_time(episode[-1])}')
        self.ui.sensorEpisodeLabel.setText(f'Sensors: {self.episode_sensors[index]}')
        self.ui.lengthEpisodeLabel.setText(f'Length: 0/{self.max_time}s')
        self.ui.timeSlider.setMinimum(0)
        self.ui.timeSlider.setMaximum(len(self.episodes[self.episode_index]) - 1)

        self.draw_plot()
        self.episode_selected = True

    def clear_frame(self):
        """
        Clear plots and all the frame/episode stats

        :return:
        """
        self.plot_scene.clear()

        self.ui.frameAmountLabel.setText(f'frame: -/-')
        self.ui.startEpisodeLabel.setText(f'Start: -')
        self.ui.endEpisodeLabel.setText(f'Stop: -')
        self.ui.minLabel.setText(f'min: -')
        self.ui.maxLabel.setText(f'max: -')
        self.ui.avLabel.setText(f'av: -')

        self.ui.frameTimeLabel.setText(f'Frame time: -')

    def draw_plot(self):
        """
        This function takes the current measurement and asks the corresponding sensor to provide imgs to visualize
        that meas. After the imgs are received the function will look at get_grid_from to see how many rows and
        columns there should be. Important that the qt_imgs and qt_pix always stay in memory by assigning them
        to the class (put self. in front)
        :return:
        """
        self.plot_scene.clear()
        text_margin = 10

        if self.episode_index < 0:
            return

        # Get the measurement and corresponding sensor to load the imgs
        current_meas = self.episodes[self.episode_index][self.frame_index]

        sensor = current_meas.sensor
        imgs = sensor.get_default_vis(current_meas.or_index)

        self.qt_imgs = [ImageQt(img) for img in imgs]
        self.qt_pix = [QPixmap.fromImage(img) for img in self.qt_imgs]

        plot_amount = len(self.qt_pix)
        grid = get_grid_form(plot_amount)
        self.logger.info(f'Current grid is: {grid}')

        # Calculate width, height and then get the grid form
        scene_size = self.plotGraphicsView.size()
        frame_width = scene_size.width()
        frame_height = scene_size.height() - text_margin
        grid_width = math.floor(frame_width / grid[0])
        grid_height = math.floor(frame_height / grid[1])

        # Populate the graphicsscene
        for index, pix in enumerate(self.qt_pix):
            frame_offset_x = grid_width * (index % grid[0])
            frame_offset_y = grid_height * (index // grid[0]) + text_margin

            img_size = pix.size()
            img_width = img_size.width()
            img_height = img_size.height()
            scale_x = grid_width / img_width
            scale_y = grid_height / img_height

            scale = scale_x if scale_x < scale_y else scale_y

            scene_img = self.plot_scene.addPixmap(pix)
            scene_img.setScale(scale)

            img_offset_x = (grid_width - img_width * scale) / (2 * scale)
            img_offset_y = (grid_height - img_height * scale) / (2 * scale)

            scene_img.setPos(img_offset_x + frame_offset_x, img_offset_y + frame_offset_y)

        # Add the sensor id on top of the scene
        scene_text = self.plot_scene.addText(str(current_meas.sensor_id))
        scene_text.setPos(2, 2)

        # Provide some extra information on the gui
        self.ui.frameTimeLabel.setText(f'Frame time: {meas_to_time(current_meas, seconds=True)}')
        self.ui.sensorLabel.setText(f'Sensor: {current_meas.sensor_id}')

    def reload_db(self):
        """
        This function removes all the sources with 'sensor' type (these contain data from the db) and then
        gets all the distincts ids from the db and creates new sources with these.
        :return:
        """
        self.clear_sources('sensor')

        id_list = self.db_bridge.get_distinct_ids(self.get_query_param())
        for id in id_list:
            self.add_source('sensor', id)

    def write_csv_current_episode(self):
        """
        Activated from the ui.saveCSVEPISODEButton, this writes the entire episode to a csv
        :return:
        """
        self.logger.info("clicked")
        if not self.episode_selected:
            self.logger.info('No episode selected')
            return
        write_csv_list_frames(self.episodes[self.episode_index], self.download_path)

    def write_csv_current_frame(self):
        """
        Activated from the ui.saveCSVFRAMEButton, this writes the single active frame to a csv
        :return:
        """
        self.logger.info("clicked")
        if not self.episode_selected:
            return
        write_csv_frame(self.episodes[self.episode_index][self.frame_index], self.download_path)


app = QtWidgets.QApplication(sys.argv)
MainWindow = MyUI()
MainWindow.show()
sys.exit(app.exec_())