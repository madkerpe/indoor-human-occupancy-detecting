from help_module.csv_helper import load_csv
from help_module.time_helper import clean_diff, abs_diff, get_time_str
from localization.processing import ImageProcessor
from datetime import datetime, timedelta
import os
import math
from PIL import Image, ImageDraw

def save_video_frames(sensor_id, measurements, FPS=28.84):
    start_time = measurements[0].timestamp
    end_time = measurements[-1].timestamp
    cur_time = start_time


    pros = ImageProcessor()

    margin = 10

    for index, meas in enumerate(measurements):
        comp = Image.new('RGB', (320 * 5 + margin * 4, 280), color=(255, 255, 255))
        pros.set_thermal_data(meas.data)

        local_time = get_time_str(meas.timestamp, microseconds=True, seconds=True)

        pros_imgs = pros.get_imgs()

        for img_index, img in enumerate(pros_imgs):
            comp.paste(img, (img_index * (320 + margin), 20))

        d = ImageDraw.Draw(comp)
        d.text((0, 0), local_time, fill=(0, 0, 0))

        img_name = f'{frame_folder}{sensor_id}_' + ('000000' + str(index))[-6:] + '.png'
        print(img_name)
        comp.save(img_name)


csv_folder = "D:/VOP_scenarios/scenarios/2_personen/"
csv_file = 'data.csv'
frame_folder = csv_folder + 'pros_frames/'

if not os.path.exists(frame_folder):
    os.mkdir(frame_folder)

data = load_csv(csv_folder + csv_file, to_numpy=True, split=True, csv_tag=False)

for key, value in data.items():
    save_video_frames(int(key), value)