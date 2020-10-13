import json

config_file = "configuration_files/calibration_configuration.json"

def add_calibration_point(name, co):
    with open(config_file, 'r+') as f:
        data = json.load(f)
        data['points'][name] = co
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()

def remove_calibration_point(name):
    with open(config_file, 'r+') as f:
        data = json.load(f)
        data['points'].pop(name, None)
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()

def get_calibration_points():
    with open(config_file, 'r') as f:
        data = json.load(f)
        return data['points']

def get_calibration_co(name):
    with open(config_file, 'r+') as f:
        data = json.load(f)
        return data['points'][name]

def save_calibration_data(calibration_points):
    with open(config_file, 'r+') as f:
        data = json.load(f)
        prev_points = data["calibration_data"]

        for point in calibration_points:
            prev_points[point["name"]] = point["img_data"]

        data["calibration_data"] = prev_points

        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()

# def save_calibration_point(calib_point_data):
#     # self.current_calibrate = {'name': name, 'co': co, 'img_data': {}, 'sensor_ids': sensor_ids}
#     with open(config_file, 'r+') as f:
#         data = json.load(f)
#         prev_points = data["calibration_data"]
#         prev_points =
#
#         for point in calibration_points:
#             prev_points[point["name"]] = point["img_data"]
#
#         data["calibration_data"] = prev_points
#
#         f.seek(0)
#         json.dump(data, f, indent=4)
#         f.truncate()


def get_calibration_sensor_ids():
    with open(config_file, 'r') as f:
        data = json.load(f)
        return data['sensor_ids']