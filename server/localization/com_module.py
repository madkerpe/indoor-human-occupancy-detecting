from flask_server import socketio
from help_module.img_helper import combine_imgs, PIL_to_64

class ComModule:
    amount_connections = 0

    def __init__(self):
        pass

    def distribute_imgs(self, id, imgs):
        img = combine_imgs(imgs)
        buf = PIL_to_64(img)
        socketio.emit('new_image', {'id': id, 'img': buf.decode('utf-8')})

    def tracker_update(self, data_dict):
        #print("tracker update")
        socketio.emit('tracker_update', data_dict)

    def localiser_update(self, coord_list):
        # print(coord_list)
        new_list = []
        for coord in coord_list['co']:
            new_list.append(list(coord))
        coord_list['co'] = new_list
        socketio.emit('localiser_update', coord_list)

    @staticmethod
    def new_connection():
        print("New client")
        """
        Connection with the socketio 'connect' event in the routes io
        """
        ComModule.amount_connections += 1

    @staticmethod
    def left_connection():
        print("Client left")
        """
            Connection with the socketio 'disconnect' event in the routes io
        """
        ComModule.amount_connections -= 1

    def any_clients(self):
        return ComModule.amount_connections >= 0