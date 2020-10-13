from flask_server import socketio, loc_bridge
from localization.com_module import ComModule
from localization.server_bridge import ServerBridge


socketio.on_event('connect', ComModule.new_connection)
socketio.on_event('disconnect', ComModule.left_connection)

socketio.on_event('reset_trackers', ServerBridge.reset_trackers)

@socketio.on('calibrate_point')
def io_calibrate_point(data):
    loc_bridge.calibrate_point(data['point'], data['ids'])