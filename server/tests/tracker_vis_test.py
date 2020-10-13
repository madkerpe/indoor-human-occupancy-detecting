from flask_server import socketio
import time
import requests
'''
def test():
    time.sleep(5)
    socketio.emit('tracker_update',{'ID':1,'position':(120,130)})
    time.sleep(1)
    socketio.emit('tracker',[{'ID':2,'position':(0,130)},{'ID':3,'position':(200,300)}])
    time.sleep(0.2)
    socketio.emit('tracker',[{'ID':1,'position':(400,130)},{'ID':2,'position':(20,50)}])
    time.sleep(1)
    for i in range(30):
        print("sending update")
        socketio.emit('tracker',[{'ID':1,'position':(400-i*6,130)}])
        time.sleep(0.2)
        '''
def test_url():
    time.sleep(5)
    print('start')
    requests.post('http://192.168.0.109:5000/tracker/update?ID=1&position_x=20&position_y=40')
    requests.post('http://192.168.0.109:5000/tracker/update?ID=2&position_x=80&position_y=40')
    time.sleep(0.1)
    requests.post('http://192.168.0.109:5000/tracker/update?ID=1&position_x=40&position_y=40')
    time.sleep(0.2)
    requests.post('http://192.168.0.109:5000/tracker/update?ID=1&position_x=60&position_y=40')
    time.sleep(0.2)
    requests.post('http://192.168.0.109:5000/tracker/update?ID=1&position_x=80&position_y=40')
    time.sleep(0.2)
    requests.post('http://192.168.0.109:5000/tracker/update?ID=1&position_x=100&position_y=50')
    time.sleep(0.2)
    requests.post('http://192.168.0.109:5000/tracker/update?ID=1&position_x=60&position_y=40')
    time.sleep(0.2)
    requests.post('http://192.168.0.109:5000/tracker/update?ID=1&position_x=150&position_y=60')
    print("done")




if __name__=="__main__":
    test_url()