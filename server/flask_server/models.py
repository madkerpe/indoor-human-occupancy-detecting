from datetime import datetime
from flask_server import db

#this class is created based on the DB relation as defined in db_create.sql
class Measurement(db.Model):
    __tablename__= 'Sensor_data'
    sensor_id = db.Column('sensor_ID',db.Integer, primary_key=True,nullable=False)
    data = db.Column('data', db.ARRAY(db.Integer), nullable=False)
    sequence_id = db.Column('sequence_ID', db.Integer)
    timestamp = db.Column('timestamp',db.DateTime, nullable=False,
                        default=datetime.utcnow,primary_key=True)
    data_type = db.Column('data_type', db.SmallInteger)

    def __repr__(self):
        return f'<Measurement :: sensor_id={self.sensor_id}, sequence_id={self.sequence_id}>'

class Measurement_test(db.Model):
    __tablename__= 'Sensor_data_test'
    sensor_id = db.Column('sensor_ID',db.Text, primary_key=True,nullable=False)
    data = db.Column('data', db.ARRAY(db.Integer), nullable=False)
    sequence_id = db.Column('sequence_ID', db.Integer)
    timestamp = db.Column('timestamp',db.DateTime, nullable=False,
                        default=datetime.utcnow,primary_key=True)
    data_type = db.Column('data_type', db.SmallInteger)

    def __repr__(self):
        return f'<Measurement :: sensor_id={self.sensor_id}, sequence_id={self.sequence_id}>'


#
# a=Measurement.query.all()
# for i in a:
#     print (i.data)
#     print(i.timestamp)