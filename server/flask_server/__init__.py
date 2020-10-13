from flask import Flask
import json
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from os.path import dirname
import logging

postgres_user = '??'
postgres_pass = '??'

with open('configuration_files\db_configuration.json', 'r') as f:
    data = json.load(f)

postgres_user = data['postgres']['username']
postgres_pass = data['postgres']['password']
postgres_db = data['postgres']['db_name']

app_path = dirname(__file__)
VOP_path = dirname(dirname(app_path))
template_path = VOP_path + '/GUI/html_templates'
static_path = VOP_path + '/GUI/static'

app = Flask(__name__, template_folder=template_path, static_folder=static_path, )
# app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgres://{postgres_user}:{postgres_pass}@localhost:5432/{postgres_db}'
app.config['SQLALCHEMY_POOL_SIZE'] = 100
db = SQLAlchemy(app)
db.get_engine().connect()
socketio = SocketIO(app, logger=False, engineio_logger=False)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

from localization.server_bridge import ServerBridge
loc_bridge = ServerBridge()

from flask_server import routes_backend
from flask_server import routes_frontend
from flask_server import routes_html
from flask_server import routes_io

