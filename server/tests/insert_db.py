from sqlalchemy import create_engine, Table, MetaData, Column, Integer, String, DateTime, ARRAY
from sqlalchemy.ext.declarative import declarative_base


engine = create_engine('postgres://postgres:Gilles@localhost:5432/VOP')
connection = engine.connect()


meta = MetaData()

table = Table('thermal_data', meta,
    Column('device_id', Integer, primary_key=True),
    Column('seq_id', Integer),
    Column('time', DateTime, primary_key=True),
    Column('data', ARRAY(Integer)))

meta.create_all(engine)

##
# meta.bind(engine)
# #
#
ins = table.insert().values(
    device_id=5,
    seq_id=4,
    data=[5,6,6]
)

connection.execute(ins)

# Retrieve data from database

# stmt = 'SELECT * FROM thermal_data'
#
# results_poxy = connection.execute(stmt)
#
# results = results_poxy.fetchall()
# print(results[0])

# Inserting



print(engine.table_names())