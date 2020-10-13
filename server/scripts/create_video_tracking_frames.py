from help_module.csv_helper import load_csv
from help_module.time_helper import clean_diff, abs_diff, get_time_str
from localization.processing import ImageProcessor
from localization.Tracker import Tracker
from localization.localiser import Localiser
from datetime import datetime, timedelta
import os
import math
from PIL import Image, ImageDraw


csv_folder = "../../scenarios/1_person_1_sensor/01/"
csv_file = 'sensor_data_shorten.csv'
frame_folder = csv_folder + 'frames_tracking/'

if not os.path.exists(frame_folder):
    os.mkdir(frame_folder)

measurements = load_csv(csv_folder + csv_file, to_numpy=True, split=False, csv_tag=False)

start_time = measurements[0].timestamp
end_time = measurements[-1].timestamp
cur_time = start_time

FPS = 30

time_diff = clean_diff(end_time, start_time)
time_jumps = math.floor(time_diff * FPS)
time_jump = 1 / FPS

meas_index = 0

tracker = Tracker()

loc_dict = {}

prev_frame = tracker.get_vis()

for i in range(time_jumps):
    print(i)
    cur_time += timedelta(seconds=time_jump)

    # cur_time > measurement
    while clean_diff(measurements[0].timestamp, cur_time) < 0:
        cur_meas = measurements.pop(0)

        if cur_meas.sensor_id not in loc_dict:
            loc_dict[cur_meas.sensor_id] = Localiser(cur_meas.sensor_id)
            loc_dict[cur_meas.sensor_id].set_tracker(tracker)
            loc_dict[cur_meas.sensor_id].calibrate_data()

        loc_dict[cur_meas.sensor_id].update(cur_meas.data, cur_meas.timestamp)
        prev_frame = tracker.get_vis()

    img_name = f'{frame_folder}' + ('000000' + str(i))[-6:] + '.png'

    prev_frame.save(img_name)