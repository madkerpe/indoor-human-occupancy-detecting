from flask import render_template, url_for, flash, redirect, request, jsonify, Response
from flask_server import app
from flask_server.models import Measurement_test, Measurement

from help_module.img_helper import fast_thermal_image, PIL_to_bytes, combine_imgs
from help_module.flask_helper import serve_pil_image
from help_module.webcam_helper import get_webcam_img
import time
from localization.processing import ImageProcessor
from PIL import Image



@app.route("/thermal_data/images", methods=['GET'])
def get_last_thermal_image():
    scaled_up = request.args.get('scale_up')
    scaled_up = 1 if scaled_up is None else int(scaled_up)

    interpolate = request.args.get('interpolate')
    interpolate = True if interpolate == "1" else False

    simulated = request.args.get('simulate')
    simulated = True if simulated == "1" else False

    print(scaled_up, interpolate)
    if simulated:
        last_result = Measurement_test.query.order_by(Measurement_test.timestamp.desc()).first()
    else:
        last_result = Measurement.query.order_by(Measurement.timestamp.desc()).first()

    img = fast_thermal_image(32, 24, last_result.data)

    print(f'Retrieved image from: {last_result.timestamp}')

    return serve_pil_image(img)

@app.route("/thermal_sensor/amount", methods=['GET'])
def count_sensors():
    amount = Measurement.query.distinct(Measurement.sensor_id).count()
    print(amount)
    return str(amount)

@app.route("/thermal_sensor/ids", methods=['GET'])
def get_ids():
    query_list = Measurement.query.distinct(Measurement.sensor_id).all()
    id_list = [meas.sensor_id for meas in query_list]
    return jsonify({"id_list": id_list})

@app.route("/thermal_sensor/<id>/last_image", methods=['GET'])
def get_sensor_last_image(id):
    processor=ImageProcessor()

    print(f'requesting last image with id={id}')
    scaled_up = request.args.get('scale_up')
    scaled_up = 1 if scaled_up is None else int(scaled_up)

    interpolate = request.args.get('interpolate')
    interpolate = True if interpolate == "1" else False

    simulated = request.args.get('simulate')
    simulated = True if simulated == "1" else False

    if simulated:
        last_result = Measurement_test.query.filter(Measurement_test.sensor_id == id).order_by(Measurement_test.timestamp.desc()).first()
    else:
        last_result = Measurement.query.filter(Measurement.sensor_id == int(id)).order_by(Measurement.timestamp.desc()).first()
    #get processed frame
    processor.process(last_result.data)
    cv2_data=processor.plot_frame()
    img = fast_thermal_image(cv2_data, scale=scaled_up)

    return Response(img)

def stream_gen(id, simulated, show_webcam=True):
    print(f'requested stream for {id}')
    processor=ImageProcessor()
    while True:
        time.sleep(.1)
        if simulated:
            last_result = Measurement_test.query.filter(Measurement_test.sensor_id == id).order_by(Measurement_test.timestamp.desc()).first()
        else:
            last_result = Measurement.query.filter(Measurement.sensor_id == id).order_by(Measurement.timestamp.desc()).first()
        # get processed frame


        yield (b'--frame\r\nContent-Type: image/png\r\n\r\n' + img_bytes + b'\r\n')

