import csv
from localization.processing import ImageProcessor
from help_module.time_helper import convert_to_datetime, get_time_str
from PIL import Image, ImageDraw
import os

pros = ImageProcessor()
data_list = []

folder_location = '../../data/'
file_name = 'bad_frames.csv'

timestamp_top_margin = 20

file_without_ext = file_name.split('.')[0]
video_folder_name = 'video_' + file_without_ext + '/'

if not os.path.exists(folder_location + video_folder_name):
    os.mkdir(folder_location + video_folder_name)

with open(folder_location + file_name) as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for index, row in enumerate(reader):
        print(row)
        thermal_data = eval(row[0])
        pros.set_thermal_data(thermal_data)
        meas_datetime = convert_to_datetime(row[1])
        local_time = get_time_str(meas_datetime, microseconds=True, seconds=True)

        centroid_frame = Image.fromarray(pros.plot_centroids(rgb=True), 'RGB')

        pros_imgs = pros.get_imgs()

        img_width = centroid_frame.size[0]
        img_height = centroid_frame.size[1]
        comp = Image.new('RGB', (img_width, img_height + timestamp_top_margin))
        d = ImageDraw.Draw(comp)
        d.text((0, 0), local_time, fill=(255, 255, 255))

        for index, img in enumerate(pros_imgs):
            comp.paste(img, (0, 20))
            comp.save(folder_location + video_folder_name + f'{index}_{str(index).zfill(5)}.png')





# ffmpeg -r 30 -f image2 -s 1500x1200 -i 70_%06d.png -vcodec libx264 -crf 10  -pix_fmt yuv420p pros.mp4