from datetime import datetime
from help_module.csv_helper import load_csv, write_csv_list_frames
from help_module.time_helper import convert_to_datetime
from localization.processing import ImageProcessor
import numpy as np
from PIL import Image

csv_file = "../../data/progression_test.csv"

pros = ImageProcessor()


#
# pcb_versions = ['v2_met_batterij', 'v2_zonder_batterij', 'pcb_Gilles', 'breadboard', 'v1', 'volledig_batterij']
#
# for file_name in pcb_versions:
#     meas = load_csv(file_name + '.csv', to_numpy=True, split=False, csv_tag=False)[0]
#     pros.set_thermal_data(meas.data)
#

meas = load_csv(csv_file, to_numpy=True, split=False, csv_tag=False)[0]
pros.set_thermal_data(meas.data)

imgs = pros.plot_contour_progression()
comp_img = Image.new('RGB', (1280 + 3 * 20, 240), color=(255,255,255))
for index, img in enumerate(imgs):
    comp_img.paste(img, (index * (320 + 20), 0))
comp_img.save('test_progression.png')
