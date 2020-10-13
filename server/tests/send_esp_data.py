import requests
import random
import time

width = 32
height = 24

test_amount = 4
device_amount = 1

sequence_array = [0] * device_amount

sensor_ids = [400, 500]
index = 0

POST_url = 'http://localhost:5000/sensor/debug'

for _ in range(test_amount):
    thermal_image = [random.randrange(0,100) for _ in range(width * height)]
    device_id = sensor_ids[index]
    index = (index + 1) % len(sensor_ids)

    json_dict = {'device_id': device_id, 'sequence': 0, 'data': thermal_image}

    r = requests.post(POST_url, json=json_dict)
    print(r.status_code)

print('Ended send_esp_data')