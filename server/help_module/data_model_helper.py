from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ARRAY, DateTime, SmallInteger
from datetime import datetime
import numpy as np
from help_module.time_helper import convert_to_datetime

Base = declarative_base()

"""
There are two similar files here, the Measurement_db is the class used to pull data from the database, 
the measurement class should act the same as the Measurement_db but has no connection with the database. This is
needed because sqlalchemy can't handle file type changes in the Measurement_db so everytime the values get copied to 
a Measurement object.
"""


class Measurement_db(Base):
    __tablename__= 'Sensor_data'
    sensor_id = Column('sensor_ID',Integer, primary_key=True,nullable=False)
    data = Column('data', ARRAY(Integer), nullable=False)
    sequence_id = Column('sequence_ID', Integer)
    timestamp = Column('timestamp',DateTime, nullable=False,
                        default=datetime.utcnow,primary_key=True)
    data_type = Column('data_type', SmallInteger)
    or_index = None
    sensor = None

    def set_or_index(self, index):
        self.or_index = index

    def set_sensor(self, sensor):
        self.sensor = sensor

    def convert_to_numpy(self):
        raise Exception('Here')
        self.data = np.array(self.data)

    def __repr__(self):
        return f'<Measurement :: sensor_id={self.sensor_id}, sequence_id={self.sequence_id}>'

class Measurement:
    def __init__(self, meas):
        self.data = meas.data
        self.sensor_id = meas.sensor_id
        self.sequence_id = meas.sequence_id
        self.timestamp = meas.timestamp
        self.data_type = meas.data_type

        self.or_index = None
        self.sensor = None

    def set_or_index(self, index):
        self.or_index = index

    def set_sensor(self, sensor):
        self.sensor = sensor

    def convert_to_numpy(self):
        self.data = np.array(self.data)

class CSV_Measurement:
    def __init__(self, row, to_numpy=True, csv_tag=True):
        if to_numpy:
            self.data = np.array(eval(row[0]))
        else:
            self.data = eval(row[0])
        self.timestamp = convert_to_datetime(row[1])
        self.sequence_id = int(row[2])
        if csv_tag:
            self.sensor_id = 'csv_' + row[3]
        else:
            self.sensor_id = row[3]
        self.or_index = None
        self.sensor = None
        self.data_type = 0

    def set_values(self, sensor_id, data, sequence_id, timestamp, data_type):
        self.sensor_id = sensor_id
        self.data = data
        self.sequence_id = sequence_id
        self.timestamp = timestamp
        self.data_type = data_type

    def set_or_index(self, index):
        self.or_index = index

    def set_sensor(self, sensor):
        self.sensor = sensor

    def convert_to_numpy(self):
        self.data = np.array(self.data)
