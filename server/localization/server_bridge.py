from localization.Tracker import Tracker
from localization.localiser import Localiser
from localization.com_module import ComModule
from help_module.calibration_helper import save_calibration_data, get_calibration_co, add_calibration_point


class ServerBridge:

    trackers = []

    def __init__(self):
        self.localization_dict = {}
        self.tracker = Tracker()
        ServerBridge.trackers.append(self.tracker)
        self.com_module = ComModule()
        self.tracker.add_visualisation(self.com_module)
        self.calibrate_data = []
        self.current_calibrate = None
        self.auto_localiser = True
        self.calibrate_index = 0

    @staticmethod
    def reset_trackers():
        """
        Called from the socketio 'reset_trackers' event defined in the routes_io
        :return:
        """
        print("resetting trackers")
        for tracker in ServerBridge.trackers:
            tracker.reset_tracker()


    def update(self, sensor_id, data, timestamp):
        """
        This is the main input of the ServerBridge, accepts thermal input and will send is the a localiser.
        :param sensor_id:
        :param data:
        :param timestamp:
        :return:
        """
        self.check_updates(sensor_id, data, timestamp)
        if sensor_id not in self.localization_dict:
            self.__add_localiser(sensor_id)
        self.localization_dict[sensor_id].update(data, timestamp)

        if self.calibrate_index > 0:
            self.calibrate_index -= 1

        if self.calibrate_index == 0 and self.current_calibrate is not None:
            self.current_calibrate = None
            print('deleted current calibrate')

    def __add_localiser(self, sensor_id, calibrate_data=None):
        """
        Creates new Localiser and add the tracker
        :param sensor_id:
        :param calibrate_data:
        :return:
        """
        print('adding localiser')
        new_localiser = Localiser(sensor_id)
        #TODO: auto calibrate? how are we gonna calibrate at the right time with the right data?
        new_localiser.calibrate_data()
        new_localiser.set_tracker(self.tracker)
        new_localiser.set_com_module(self.com_module)

        self.localization_dict[sensor_id] = new_localiser

    def calibrate_point(self, name,  sensor_ids):
        """
        The self.current_calibrate is a dict that contains information about the points that need to be calibrated.
        When it is not None the check_calibrate function will safe the img in the self.current_calibrate when
        the right sensor sends its information
        :param name:
        :param sensor_ids:
        :return:
        """

        co = get_calibration_co(name)
        if self.current_calibrate is None and len(sensor_ids) > 0:
            self.current_calibrate = {'name': name, 'co': co, 'img_data': {}, 'sensor_ids': sensor_ids}
            self.calibrate_index = 10
            print("Set calibration point ready in server_bridge")
        else:
            print('WARNING there is still a calibration point active')

    def check_updates(self, sensor_id, data, timestamp):
        self.check_calibrate(sensor_id, data, timestamp)

    def check_calibrate(self, sensor_id, data, timestamp):
        """
        This function checks if the current update contains useful data for calibration.
        :param sensor_id:
        :param data:
        :param timestamp:
        :return:
        """
        if self.current_calibrate is not None:
            if sensor_id not in self.current_calibrate['img_data'] and sensor_id in self.current_calibrate['sensor_ids']:
                processor = self.localization_dict[sensor_id].processor
                processor.set_thermal_data(data)
                data = processor.get_calib_points()
                print("calib point =" + str(data))
                self.current_calibrate['img_data'][sensor_id] = data

            print(f'Current length img data: {len(self.current_calibrate["img_data"])}')
            print(f'Current lenght sensor_ids: {len(self.current_calibrate["sensor_ids"])}')

            if len(self.current_calibrate['img_data']) == len(self.current_calibrate['sensor_ids']):
                print("Saved the calibration point")
                # self.current_calibrate = {'name': name, 'co': co, 'img_data': {}, 'sensor_ids': sensor_ids}
                self.calibrate_data.append(self.current_calibrate)
                save_calibration_data(self.calibrate_data)
                self.current_calibrate = None

    def bridge_save_cal_data(self):
        save_calibration_data(self.calibrate_data)
        print("Saved loc data")

