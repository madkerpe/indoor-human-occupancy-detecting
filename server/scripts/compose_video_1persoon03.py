from datetime import datetime
from help_module.csv_helper import load_csv, write_csv_list_frames
from help_module.time_helper import convert_to_datetime
from help_module.csv_helper import load_csv
from help_module.time_helper import clean_diff, abs_diff, get_time_str
from localization.processing import ImageProcessor
from localization.Tracker import Tracker
from localization.localiser import Localiser
from datetime import datetime, timedelta, date, time
import os
import math
from PIL import Image, ImageDraw
import time as time_module


scenario_folder = 'D:/VOP_scenarios/scenarios/'
cur_scenario = '1_persoon/'

vol_scen_folder = scenario_folder + cur_scenario

rgb_folder = vol_scen_folder + 'rgb_frames/'

csv_file = vol_scen_folder + 'sensor_data.csv'
frame_folder = vol_scen_folder + 'comp_frames/'

if not os.path.exists(frame_folder):
    os.mkdir(frame_folder)

measurements = load_csv(csv_file, to_numpy=True, split=False, csv_tag=False)


video_start = datetime.combine(measurements[0].timestamp.date(), time(hour=12, minute=55, second=18)).timestamp()
video_stop = datetime.combine(measurements[0].timestamp.date(), time(hour=13, minute=00, second=2)).timestamp()

cur_time = video_start

time_diff = video_stop - video_start
time_jumps = 4229
time_jump = time_diff / time_jumps

meas_index = 0

tracker = Tracker()

loc_dict = {}

prev_frame = tracker.get_vis()

rgb_frame_start_index = 6

test_start = measurements[0].timestamp.timestamp()

comp_img = Image.new('RGB', (1500, 480+720))
pros_imgs = []
for i in range(time_jumps):
    print(i)
    cur_time += time_jump

    while measurements[0].timestamp.timestamp() < cur_time:
        cur_meas = measurements.pop(0)

        if cur_meas.sensor_id not in loc_dict:
            loc_dict[cur_meas.sensor_id] = Localiser(cur_meas.sensor_id)
            loc_dict[cur_meas.sensor_id].set_tracker(tracker)
            loc_dict[cur_meas.sensor_id].calibrate_data()

        loc_dict[cur_meas.sensor_id].update(cur_meas.data, cur_meas.timestamp)

        pros_imgs = []
        for locs in loc_dict.values():
            pros_imgs.append(locs.get_scaled_img((600,480)))


        prev_frame = tracker.get_vis()

    rgb_img = Image.open(rgb_folder + ('000000' + str(i + rgb_frame_start_index))[-6:] + '.png').rotate(180)

    comp_img.paste(rgb_img, (0, 480))
    comp_img.paste(prev_frame, (0, 0))
    if len(pros_imgs) > 0:
        comp_img.paste(pros_imgs[0], (754, 0))

    d = ImageDraw.Draw(comp_img)
    local_time = time_module.strftime('%Y-%m-%d %H:%M:%S', time_module.localtime(cur_time))
    d.text((10, 490), local_time, fill=(255,0,0))
    img_name = f'{frame_folder}' + ('000000' + str(i))[-6:] + '.png'

    comp_img.save(img_name)