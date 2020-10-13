from localization.Person import Person
import numpy as np
from scipy.optimize import linear_sum_assignment
from collections import deque
import time
import math
from collections import defaultdict

from PIL import Image, ImageDraw
from help_module.img_helper import get_bounding_box
from random import randint

class Tracker:
    def __init__(self):
        self.id_counter = 0
        self.persons = []
        self.listeners = []
        self.last_tracker_timestamp = time.time()

        self.dist_thresh = 75
        self.SMA_window = deque([]) #FIFO-queue
        self.SMA_window_length = 10
        self.SMA = 0

        self.tracker_colors = {}
        self.prev_points = defaultdict(list)
        

    def add_visualisation(self,vis):
        assert(hasattr(vis, "tracker_update")) # must have update method to send new positions to
        self.listeners.append(vis)

    def update(self, positions, timestamp):
        '''
        core function of the tracker
        links positions to existing or new persons
        updates all persons and creates new ones
        updates visualisation listeners
        :param timestamp: timestamp of positions
        :param positions: list of np arrays (x,y)
        :return: None
        '''

        # print(f'positions: {positions}')
        # positions = np.array(positions['co'])
        # print(positions)

        timestamp = timestamp.timestamp()
        if self.last_tracker_timestamp is None:
            self.last_tracker_timestamp = timestamp

        dist_matrix = self.get_matrix(positions,timestamp)
        tups, new_positions = self.get_assignment(dist_matrix)
        updated_pers_index = []
        for pers_index, pos_index in tups:
            filter = self.persons[pers_index].kalmanfilter
            filter.predict(timestamp)

            #if its not yet time to show, decrement TTS
            # print(self.persons[pers_index])
            if self.persons[pers_index].TTS > 0:
                last_person_timestamp = filter.previous_timestamp
                # print(timestamp-last_person_timestamp)
                self.persons[pers_index].TTS -= (timestamp - last_person_timestamp)

            filter.update(positions[pos_index], timestamp) #!important this must be after TTS update because stamp is updated
            ##quick fix for Gilles##
            #TODO: check & test!
            self.persons[pers_index].locations[timestamp] = self.persons[pers_index].get_location()
            #################
            updated_pers_index.append(pers_index)
            #reset the TTL to the initial value
            self.persons[pers_index].TTL = Person.TTL_initial_value

        #decrement all the other Person's TTL
        for pers_index in range(len(self.persons)):
            if pers_index not in updated_pers_index:
                if (self.last_tracker_timestamp < timestamp):
                    self.persons[pers_index].TTL -= (timestamp - self.last_tracker_timestamp)

        for person in self.persons:
            if person.TTL <= 0:
                self.persons.remove(person)

        for pos_index in new_positions:
            self.persons.append(Person(self.id_counter, positions[pos_index], timestamp))
            self.id_counter+=1


        self._add_SMA_average()
        self.listeners_update()
        self.last_tracker_timestamp = timestamp
        # print("tracker updated")

    def get_matrix(self,positions,timestamp):
        '''
        creates probability matrix for all persons and positions
        :param positions: see update
        :return: to be specified
        '''

        matrix = np.zeros((len(self.persons),len(positions)))
        for i in range(len(self.persons)):
            for j in range(len(positions)):
                matrix[i,j]= self._dist(self.persons[i], positions[j], timestamp)
        return matrix


    def get_assignment(self,dist_matrix,greedy = False):
        '''
        makes global optimal assignment of the prop matrix
        :param dist_matrix:
        :return: a tuple , first part is an array of tupples person_index, position_index
                second part are just positions
        '''
        if not greedy:
            person_index, position_index = linear_sum_assignment(dist_matrix)
        else:
            person_index = []
            position_index = []
            rows = dist_matrix.shape[0]
            cols = dist_matrix.shape[1]

            total_match = min([rows, cols])
            if total_match <=0:
                max_value = -1
            else:
                max_value = np.max(dist_matrix)

            for idx in range(0, total_match):
                min_idx = np.unravel_index(np.argmin(dist_matrix, axis=None), dist_matrix.shape)
                if not dist_matrix[min_idx] == max_value:
                    person_index.append(min_idx[0])
                    position_index.append(min_idx[1])
                    dist_matrix[min_idx[0], :] = max_value
                    dist_matrix[:, min_idx[1]] = max_value

        tups = zip(person_index,position_index)
        new_objects = []
        for i in range(dist_matrix.shape[1]):
            if not i in position_index:
                new_objects.append(i)
        return tups, new_objects

    def listeners_update(self):
        '''
        sends new positions to listeners
        :return:
        '''
        vis_dict = {}
        for person in self.persons:
            if person.TTS <= 0: #and TTL > TTL_init - liveness
                sp1 = round(person.kalmanfilter.x[1], 2)
                sp2 = round(person.kalmanfilter.x[3], 2)
                ttl_round = round(person.TTL, 2)
                vis_dict[person.ID] = {'position':(person.get_location()[0],person.get_location()[1]), 'timelived': ttl_round, 'v_x': sp1, 'v_y': sp2, 'SMA' : self.SMA}

        for vis_object in self.listeners:
            vis_object.tracker_update(vis_dict)

    def _add_SMA_average(self):
        if len(self.SMA_window) < self.SMA_window_length:
            self.SMA_window.append(len(self.persons))
        else:
            self.SMA_window.popleft()
            self.SMA_window.append(len(self.persons))

        self.SMA = np.mean(np.asarray(self.SMA_window))

        


    def _dist(self, person, y, timestamp):
        '''
        for the moment this is just the euclidean distance which means less is more..
        :param filter: kalman of person
        :param y: 2D np array
        :return:
        '''
        filter = person.kalmanfilter
        x,P = filter.get_prediction(timestamp)
        pos = np.array([x[0],x[2]])
        line = y-pos
        dist = np.sqrt(np.sum(np.power(pos-y,2)))
        vel = np.array([filter.x[1],filter.x[3]])
        speed = np.sqrt(np.sum(np.power(vel,2)))
        angle = math.atan(vel[1]/vel[0])- math.atan(line[1]/line[0])
        abs_angle = math.fabs(angle)
        '''print("------stats-----")
        print(line)
        print(vel)
        print(abs_angle)
        print(dist)
        print(self.dist_thresh*speed)'''

        if dist < self.dist_thresh: #*speed:
            dist *= (Person.TTL_initial_value+1- person.TTL)/ (Person.TTL_initial_value+1) #favor long living objects by multiplying
            #dist *= angle
            return dist
        else:
            return 100000 # math.inf isn't handled by the hungarian algorithm so choose a random value that's never reached

    def get_vis(self):
        img = Image.open("D:/VOP_scenarios/tracker_imgs/layout_even.png")
        d = ImageDraw.Draw(img)

        for person in self.persons:
            box1 = get_bounding_box((person.get_location()[1], person.get_location()[0]))
            if person.ID in self.tracker_colors:
                color = self.tracker_colors[person.ID]
            else:
                color = (randint(0, 255), randint(0, 255), randint(0, 255))
                self.tracker_colors[person.ID] = color

            prev_points = list(person.locations.values())[-10:]
            print(f'amount prev points: {len(prev_points)}')
            print(prev_points)
            for i in range(len(prev_points) - 1):
                if prev_points[i] is not None and prev_points[i + 1] is not None:
                    cur_point = (prev_points[i][1], prev_points[i][0])
                    next_point = (prev_points[i + 1][1], prev_points[i + 1][0])
                    d.line([cur_point, next_point], fill=color, width=3)

            d.ellipse(box1, fill=color)

        return img


    def __repr__(self):
        s = ("____TRACKER STATE_____ \n")
        s += "moving average: " 
        s += self.SMA 
        s += "\n"
        for person in self.persons:
            s += person.__repr__()
            s += "\n"
        return s

    def reset_tracker(self):
        '''
        This function resets the whole state of the tracker
        '''
        print("tracker reset by tracker")
        self.SMA_window = deque([])
        self.SMA = 0.0 
        self.id_counter = 0
        self.persons = []
        self.last_tracker_timestamp = time.time()


if __name__ == "__main__":
    t0 = time.time()

    t = Tracker()
    t.update([np.array([1.,2])], t0)
    print(t)
    t.update([np.array([2.,3]), np.array([5.,6])], t0 + 1)
    print(t)
    t.update([np.array([3.,4]), np.array([3.,5])], t0 + 2)
    print(t)
    t.update([ np.array([5.,6])], t0 + 3)
    print(t)