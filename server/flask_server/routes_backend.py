from flask import render_template, url_for, flash, redirect, request, jsonify
from flask_server import app, db, socketio, loc_bridge
from flask_server.models import Measurement, Measurement_test
import json
import math
from help_module.webcam_helper import config_webcam_ip, save_webcam_frame, start_webcams, remove_webcam, stop_webcams
from help_module.calibration_helper import add_calibration_point, get_calibration_points, remove_calibration_point, get_calibration_co
import datetime

@app.route('/sensor/debug', methods=['POST'])
def receive_sensor_debug():
    data = request.json
    # print(data)
    # print("---")
    data['data'] = [0 if math.isnan(a) else a * 5 for a in data['data']]
    # print(data["data"])
    new_db_data = Measurement(sensor_id=data["device_id"], data=data["data"], sequence_id=data["sequence"], data_type=2)
    db.session.add(new_db_data)
    db.session.commit()

    # socketio.emit('new_image', {'device_id': data['device_id']})
    # save_webcam_frame(new_db_data)
    # print(data['data'])
    loc_bridge.update(data["device_id"], data["data"], new_db_data.timestamp)

    return "Hello World!"

@app.route('/sensor/simulate', methods=['POST'])
def receive_simulate():
    # print("Simulated request")
    data = request.json
    new_db_data = Measurement_test(sensor_id=data["device_id"], data=data["data"], sequence_id=data["sequence"], data_type=0)
    db.session.add(new_db_data)
    db.session.commit()

    # socketio.emit('new_image', {'device_id': data['device_id']})

    loc_bridge.update(data["device_id"], data["data"], new_db_data.timestamp)

    return "Succes"

@app.route('/sensor/simulate_no_save', methods=['POST'])
def receive_simulate_no_save():
    # print("Simulated request")
    data = request.json

    loc_bridge.update(data["device_id"], data["data"], datetime.datetime.now())

    return "Succes"


@app.route('/sensor/bits', methods=['POST'])
def receive_sensor_bits():
    data = request.json
    socketio.emit('new_image', {'device_id': data['device_id']})
    print(data)
    data['data'] = [0 if math.isnan(a) else a for a in data['data']]
    print(data)

    db.session.add(data)
    db.session.commit()
    print(data)

    print('NEW post request')

    return "Hello World!"


@app.route('/sensor/raw', methods=['POST'])
def test_cbor():
    print("============== CBOR Test ================")
    data = request.get_data()
    print(data)
    sensor_data = [int(a) for a in data]
    sensor_id = sensor_data[0]
    seq_id = sensor_data[1]
    thermal_data = sensor_data[2:]

    new_db_data = Measurement(sensor_id=sensor_id, data=thermal_data, sequence_id=seq_id, data_type=0)
    db.session.add(new_db_data)
    db.session.commit()

    socketio.emit('new_image', {'device_id': sensor_id})

    print(" CBOR STOP ")
    return 'Hello'

@app.route('/data/last', methods=['GET'])
def send_data():
    last_result = Measurement.query.order_by(Measurement.timestamp.desc()).first()
    ret_json = {"data":last_result.data, "time":last_result.timestamp, "sensor_id": last_result.sensor_id}
    print(last_result)
    return jsonify(ret_json)

@app.route('/webcam/setip', methods=['POST'])
def configure_webcam_ip():
    sensor_id = request.form.get('sensor_id')
    ip = request.form.get('ip')
    print(sensor_id)
    print(ip)
    if sensor_id is None or ip is None:
        return "Invalid request"

    config_webcam_ip(int(sensor_id), ip)

    return redirect(url_for('config_webcams'))

@app.route('/webcam/start', methods=['GET'])
def start_webcams_req():
    start_webcams()
    return redirect(url_for('config_webcams'))

@app.route('/webcam/stop', methods=['GET'])
def stop_webcams_req():
    stop_webcams()
    return redirect(url_for('config_webcams'))

@app.route('/webcam/<sensor_id>/delete', methods=['GET'])
def delete_webcam(sensor_id):
    remove_webcam(sensor_id)
    return redirect(url_for('config_webcams'))

@app.route('/config/calibrate/addpoint', methods=['POST'])
def config_add_calibration_point():
    name = request.form.get('name')
    co_x = int(request.form.get('xco'))
    co_y = int(request.form.get('yco'))
    print(f'Adding calibration point: ({co_x}, {co_y})')

    add_calibration_point(name, (co_x, co_y))
    return redirect(url_for('config_calibrate'))

@app.route('/config/calibrate/<pointname>/delete', methods=['GET'])
def config_remove_calibration_point(pointname):
    remove_calibration_point(pointname)
    # loc_bridge.calibrate_point((co_x, co_y))
    return redirect(url_for('config_calibrate'))

@app.route('/config/calibrate/<pointname>/start', methods=['GET'])
def config_start_calibration_point(pointname):
    co = get_calibration_co(pointname)
    loc_bridge.calibrate_point(pointname, co)
    return redirect(url_for('config_calibrate'))

@app.route('/config/calibrate/save', methods=['GET'])
def config_save_calibration_data():
    loc_bridge.bridge_save_cal_data()
    return redirect(url_for('config_calibrate'))



