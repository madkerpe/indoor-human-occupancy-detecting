from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from help_module.data_model_helper import Measurement_db, Base, CSV_Measurement
import json

class DB_Bridge:
    def __init__(self):
        with open(r'..\configuration_files\db_configuration.json', 'r') as f:
            data = json.load(f)

            postgres_user = data['postgres']['username']
            postgres_pass = data['postgres']['password']
            postgres_db = data['postgres']['db_name']

        self.engine = create_engine(f'postgres://{postgres_user}:{postgres_pass}@localhost:5432/{postgres_db}')
        Base.metadata.create_all(bind=self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def get_distinct_ids(self):
        sensor_ids = self.session.query(Measurement_db).distinct(Measurement_db.sensor_id).all()
        id_list = [meas.sensor_id for meas in sensor_ids]

        return id_list

    def get_distinct_ids(self, param):
        basic_query = self.session.query(Measurement_db)

        if param['act_start']:
            basic_query = basic_query.filter(Measurement_db.timestamp > param['time_start'])

        if param['act_stop']:
            basic_query = basic_query.filter(Measurement_db.timestamp < param['time_stop'])

        sensor_ids = basic_query.distinct(Measurement_db.sensor_id).all()

        id_list = [meas.sensor_id for meas in sensor_ids]

        return id_list

    def get_values(self, sensor_id, param):
        basic_query = self.session.query(Measurement_db).filter(Measurement_db.sensor_id == sensor_id)

        if param['act_start']:
            basic_query = basic_query.filter(Measurement_db.timestamp > param['time_start'])

        if param['act_stop']:
            basic_query = basic_query.filter(Measurement_db.timestamp < param['time_stop'])

        sensor_values = basic_query.order_by(Measurement_db.timestamp.desc()). \
            limit(param['amount_limit']).all()

        return sensor_values