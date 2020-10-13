from flask_server import app, socketio
import socket

run_local = True

ip_adresses = socket.gethostbyname_ex(socket.gethostname())[-1]
local_ip = None

for ip_adr in ip_adresses:
    if ip_adr.split('.')[2] == '0' or ip_adr.split('.')[2] == '1':
        local_ip = ip_adr
        break


if __name__ == '__main__':
    if run_local:
        socketio.run(app, debug=True, host='localhost')
    else:
        socketio.run(app, debug=True, host=local_ip)