"""
This files convert a database (from pgadmin) to a csv that contains 3 columns: the centroids, epoch time and local time
"""


import csv
from localization.processing import ImageProcessor
from help_module.time_helper import convert_to_datetime, get_time_str

pros = ImageProcessor()
data_list = []

folder_location = '../../data/'
file_name = '19042019.csv'

with open(folder_location + file_name) as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for index, row in enumerate(reader):
        # print(row)
        # print(index)
        thermal_data = eval(row[1])
        centroids = pros.process(thermal_data)
        meas_datetime = convert_to_datetime(row[3])
        epoch_time = meas_datetime.timestamp()
        local_time = get_time_str(meas_datetime, microseconds=True)
        data_list.append([centroids, epoch_time, local_time])

with open(folder_location + 'centroid_' + file_name, 'w+', newline='') as csvfile:
    writer = csv.writer(csvfile)
    for row in data_list:
        writer.writerow(row)
