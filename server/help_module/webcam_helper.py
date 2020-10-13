import json
import cv2
from PIL import Image
import os

config_file = "configuration_files/webcam_configuration.json"
webcam_dict = {}
recording = False
rgb_database_loc = 'D:/Programmeer projecten/VOP/server/rgb_database'


def start_webcams(sensor_ids=None):
    global webcam_dict
    global recording

    recording = True
    stop_webcams()

    with open(config_file, 'r+') as f:
        data = json.load(f)
        list_webcams = data['webcams']

        for sensor_id, ip in list_webcams.items():
            webcam_dict[sensor_id] = cv2.VideoCapture(ip)


def stop_webcams():
    global webcam_dict
    global recording
    recording = False
    for sensor_id, capture in webcam_dict.items():
        capture.release()
    webcam_dict = {}


def config_webcam_ip(sensor_id, webcam_ip):
    with open(config_file, 'r+') as f:
        data = json.load(f)
        list_webcams = data['webcams']
        list_webcams[str(sensor_id)] = webcam_ip
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()


def get_values():
    with open(config_file, 'r') as f:
        data = json.load(f)
        ip_list = data['webcams']
        return ip_list


def save_webcam_frame(meas):
    if '-1' in webcam_dict:
        print("found webcam for sensor")
        capture = webcam_dict['-1']
        s, img = capture.read()
        if s:
            filename = meas_to_filename(meas, sensor_id='-1')
            cv2.imwrite(filename, img)
            print('saving webcam frame')
        else:
            print("frame was not valid")

    if str(meas.sensor_id) in webcam_dict:
        print("found webcam for sensor")
        capture = webcam_dict[str(meas.sensor_id)]
        s, img = capture.read()
        if s:
            filename = meas_to_filename(meas)
            cv2.imwrite(filename, img)
            print('saving webcam frame')
        else:
            print("frame was not valid")

def meas_to_filename(meas, sensor_id=None):
    if sensor_id is None:
        return f'{rgb_database_loc}/{meas.timestamp.strftime("%Y%m%d%H%M%S%f%z").replace("+", "")}_{meas.sensor_id}.jpg'
    else:
        return f'{rgb_database_loc}/{meas.timestamp.strftime("%Y%m%d%H%M%S%f%z").replace("+", "")}_{sensor_id}.jpg'

def get_webcam_img(meas, sensor_id=None):
    filename = meas_to_filename(meas, sensor_id=sensor_id)
    if not os.path.isfile(filename):
        return None
    img = Image.open(filename)
    return img

def remove_webcam(sensor_id):
    with open(config_file, 'r+') as f:
        data = json.load(f)
        list_webcams = data['webcams']
        list_webcams.pop(str(sensor_id), None)
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()


def is_recording():
    return recording


if __name__ == "__main__":
    config_file = '../configuration_files/webcam_configuration.json'