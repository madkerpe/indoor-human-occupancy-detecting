import csv
import numpy as np
from help_module.data_model_helper import CSV_Measurement
from datetime import datetime, timedelta

def process_csv_row(row):
    '''
    this is a helper function used in read_data
    :param row:  a list of strings which are obtained from reading a csv line
    :return:  a np.array of int or int[]
    '''
    return [np.array(eval(row[0])),row[1], eval(row[2]),eval(row[3])]

def read_data(filename,start=0,end=None):
    """
    this function reads sesor data from a csv file
    TODO data-type is not yet read
    :param filename:
    :param start:
    :param end:
    :return: returns an array of np.arrays with sensor_data : [data, timestamp,seq_ID,sensor_ID]
    """
    if end is None:
        end = 10000000  # random high value
    data = []
    with open(filename,'r') as csvfile:
        reader=csv.reader(csvfile,delimiter=',')
        for index,row in enumerate(reader):
            if start<index and index <end:
                data.append(process_csv_row(row))
    return data


def load_csv(filename, to_numpy=True, split=False, csv_tag=True):
    """
    This function takes in a filename and creates a list of CSV_Measurements
    :param filename: csv filename
    :return: the list
    """
    if split:
        data = {}
    else:
        data = []

    with open(filename) as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for index, row in enumerate(reader):
            if index != 0 and row != '':
                n_csv = CSV_Measurement(row, to_numpy=to_numpy,csv_tag=csv_tag)
                if split:
                    if n_csv.sensor_id in data:
                        data[n_csv.sensor_id].append(n_csv)
                    else:
                        data[n_csv.sensor_id] = [n_csv]
                else:
                    data.append(n_csv)
    return data


def write_csv_list_frames(frames, path):
    '''
    this is a helper function, it saves the selected frames to a file
    :param frames: a list of Measurement objects (ORM class)
    :param path: path to folder
    :return:
    '''
    frame = frames[0]
    frame_time = frame.timestamp
    frame_time_arr = (str(frame_time)).replace('-', ',').replace('.', ',').replace(' ', ',').replace(':',',').split(',')
    time = frame_time_arr[0] + frame_time_arr[1] + frame_time_arr[2] + '-' + frame_time_arr[3] + frame_time_arr[4] + frame_time_arr[5]
    filename = path + 'sensor_data_episode' + '_' + time + '_' + str(frame.sensor_id) + '.csv'

    print('filename=' + filename)

    with open(filename, 'w', newline='') as outfile:
        writer = csv.writer(outfile, delimiter=',')
        writer.writerow(['data', 'timestamp', 'sequence_ID', 'sensor_ID', 'data_type'])
        for frame in frames:
            writer.writerow([list(frame.data), frame.timestamp, frame.sequence_id, frame.sensor_id, frame.data_type])
    print('csv saved')


def write_csv_frame(frame, path):
    '''
    this is a helper function, it saves the selected frame to a file
    :param frames: a  Measurement objects (ORM class)
    :param path: path to folder
    :return:
    '''
    frame_time = frame.timestamp
    frame_time_arr = (str(frame_time)).replace('-', ',').replace('.', ',').replace(' ', ',').replace(':', ',').split(
        ',')
    time = frame_time_arr[0] + frame_time_arr[1] + frame_time_arr[2] + '-' + frame_time_arr[3] + frame_time_arr[4] + \
           frame_time_arr[5]
    filename = path + 'sensor_data_frame' + '_' + time + '_' + str(frame.sensor_id) + '.csv'
    print('filename=' + filename)
    with open(filename, 'w', newline='') as outfile:
        writer = csv.writer(outfile, delimiter=',')
        writer.writerow(['data', 'timestamp', 'sequence_ID', 'sensor_ID', 'data_type'])
        writer.writerow([list(frame.data), frame.timestamp, frame.sequence_id, frame.sensor_id, frame.data_type])
    print('csv saved')

def load_csv_tracker_path(fname):
    path = []
    cur_time = datetime.now()
    with open(fname) as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for index, row in enumerate(reader):
            if index == 0:
                continue
            co_x = float(row[0])
            co_y = float(row[1])
            seconds_delta = float(row[2])
            time_delta = timedelta(seconds=seconds_delta)
            cur_time += time_delta
            path.append((np.array([co_x, co_y]), cur_time))

    return path