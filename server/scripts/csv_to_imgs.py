from help_module.csv_helper import load_csv
from help_module.img_helper import raw_color_plot, processed_color_plot, fast_thermal_image
from help_module.time_helper import convert_to_datetime, abs_diff, clean_diff
from help_module.webcam_helper import get_webcam_img
from datetime import  datetime, timedelta
from PIL import Image

sensor_ids = [6, 9]

img_margin = 20
sample_amount = 3

webcam_size = (320, 180)


def find_closest_time_index(meas_list, ref_time):
    min_diff = float('inf')
    min_index = -1
    for index, meas in enumerate(meas_list):
        diff = clean_diff(ref_time, meas.timestamp)
        if diff < min_diff and diff > 0:
            min_diff = diff
            min_index = index

        if diff < 0:
            break

    return min_index

def find_closest_time(meas_list, ref_time, start_index):
    index = start_index - 1
    min_diff = abs_diff(ref_time, meas_list[index].timestamp)
    min_index = index
    index += 1
    while index < len(meas_list):
        diff = abs_diff(ref_time, meas_list[index].timestamp)
        if diff < min_diff:
            min_diff = diff
            min_index = index
            index += 1
        else:
            break

    return min_index

measurements = [load_csv(f'files/csv/{sensor_id}.csv', csv_tag=False) for sensor_id in sensor_ids]
cur_indices = [0] * len(measurements)


start_time = max([meas[0].timestamp for meas in measurements])
end_time = min([meas[-1].timestamp for meas in measurements])

time_diff = (end_time - start_time).seconds - 1
FPS = 20
amount_sensors = len(sensor_ids)
amount_extra_webcams = 1


start_index = 424
frame_time_increase = timedelta(milliseconds=1000/FPS)
cur_time = start_time + start_index * frame_time_increase

for extra_time in range(start_index, time_diff * FPS):
    print(extra_time)
    cur_time += frame_time_increase

    cur_indices = [find_closest_time(meas, cur_time, cur_index) for meas, cur_index in zip(measurements, cur_indices)]

    raw_imgs = [fast_thermal_image(meas[index].data, smooth=False, side=False) for meas, index in zip(measurements, cur_indices)]
    smooth_imgs = [fast_thermal_image(meas[index].data, smooth=True, side=False) for meas, index in zip(measurements, cur_indices)]
    proc_imgs = [processed_color_plot(meas[index].data, mtplotlib=False, to_pil=True) for meas, index in zip(measurements, cur_indices)]

    webcam_imgs = [get_webcam_img(meas[index]) for meas, index in zip(measurements, cur_indices)]
    extra_webcams = [get_webcam_img(meas[index], sensor_id=-1) for meas, index in zip(measurements, cur_indices)]
    extra_webcam = None

    rescaled_webcam = [img.resize((320, 180)) if img is not None else None for img in webcam_imgs]

    for webcam in extra_webcams:
        if webcam is not None:
            extra_webcam = webcam
            break

    img_width = 1244 + amount_sensors * 340
    img_height = (240 + 20) * 2 + 180

    comp = Image.new('RGB', (img_width, img_height))

    for index in range(amount_sensors):
        comp.paste(raw_imgs[index].transpose(Image.FLIP_LEFT_RIGHT), ((320 + 20) * index, 0))
        comp.paste(proc_imgs[index].transpose(Image.FLIP_LEFT_RIGHT), ((320 + 20) * index, 240 + 20))
        if rescaled_webcam[index] is not None:
            comp.paste(rescaled_webcam[index], ((320 + 20) * index, (240 + 20) * 2))

    if extra_webcam is not None:
        resc = extra_webcam.resize((1244, 700))
        comp.paste(resc, (amount_sensors * 340, 0))


    comp.save(f'files/img/full/{str(extra_time - start_index).zfill(5)}.png')
