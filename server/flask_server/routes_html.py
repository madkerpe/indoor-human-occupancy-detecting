from flask import render_template, url_for, flash, redirect, request, jsonify
from flask_server import app
from flask_server.models import *
from help_module.webcam_helper import get_values
from help_module.calibration_helper import get_calibration_points, get_calibration_sensor_ids

@app.route("/")
def home():
    return redirect(url_for('get_debug_screen'))

@app.route("/view/thermal_data")
def get_debug_screen():
    return render_template('view_thermal_data.html')

@app.route("/view/stream_test")
def get_test_stream_screen():
    return render_template('test_stream.html')

@app.route("/view/localiser")
def get_view_localiser():
    return render_template('view_localiser.html')

@app.route("/view/tracker")
def get_view_tracker():
    return render_template('view_tracker.html')

@app.route("/view/heatmap")
def get_view_heatmap():
    return render_template('view_heatmap.html')

@app.route("/view/tracing")
def get_view_tracing():
    return render_template('view_tracing.html')

@app.route("/socketio_test")
def get_socketio_test():
    return render_template('test_socketio.html')

@app.route("/main")
def get_main():
    return render_template('main.html')

@app.route('/config/webcams')
def config_webcams():
    current_webcams = get_values()
    return render_template('config_webcam.html', current_webcams=current_webcams)

@app.route('/config/calibrate')
def config_calibrate():
    current_points = get_calibration_points()
    sensor_ids = get_calibration_sensor_ids()
    return render_template('config_calibrate.html', current_points=current_points, sensor_ids=sensor_ids)

@app.route('/config/tracker')
def config_tracker():
    current_points = get_calibration_points()

    return render_template('config_tracker.html')