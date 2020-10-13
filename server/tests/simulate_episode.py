import threading
import requests
import random

from help_module.csv_helper import load_csv

POST_url = "http://localhost:5000/sensor/simulate_no_save"

def create_timing_list(data, id_method="csv_value", id_list=None, speed_up=1):
    """
    Create a list to feed into the send_request function. This function assigns the sensor_id to the
    values and calculates the time diff between two requests.

    :param data:
    :param random_id:
        "csv_value": The requests will be send with the sensor_id specified in data
        "user_spec": when you want to manually change the id
        "id_list": requires that id_list is not None, loops through that lists and give those ids
    :param amount_id:
    :return:
    """
    timing_list = []

    index_id = 0

    for index in range(1, len(data)):
        add_dict = {}

        if id_method == "csv_value":
            add_dict['device_id'] = data[index].sensor_id
        elif id_method == "user_spec":
            add_dict['device_id'] = 65
        elif id_method == "id_list":
            add_dict['device_id'] = id_list[index_id]
            index_id = (index_id + 1) % len(id_list)

        add_dict['data'] = data[index].data
        add_dict['sequence'] = data[index].sequence_id
        time_diff = ((data[index].timestamp - data[index - 1].timestamp).microseconds / 1000000) / speed_up

        timing_list.append((time_diff, add_dict))

    return timing_list

def send_request(timer_list):
    if len(timer_list) > 0:
        json_data = timer_list.pop(0)[1]
        next_time = timer_list[0][0]
        timer = threading.Timer(next_time, send_request, [timer_list])
        timer.start()

        r = requests.post(POST_url, json=json_data)
        if r.status_code == 200:
            print(f'OK: from sensor_id {json_data["device_id"]}')
        else:
            print(r.status_code)


if __name__ == "__main__":
    csv_folder = 'E:/VOP_backup/2_personen/'
    csv_file = "shortened.csv"

    csv_data = load_csv(csv_folder+csv_file, to_numpy=False)

    timing_list = create_timing_list(csv_data, speed_up=1)

    timer = threading.Timer(0, send_request, [timing_list])
    timer.start()
    print("exit")