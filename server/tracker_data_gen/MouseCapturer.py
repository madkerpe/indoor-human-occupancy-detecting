import pyautogui
import time
import cv2
import csv
import numpy as np
import math
import matplotlib.image as im
import matplotlib.pyplot as plt
import argparse

'''
this class allows to generate a path on the layout and visualises it on the fly, to add a new waypoint at the current cursorposition: press anter
to stop generating new points: move te cursor away (100px) from the screen and press enter, then a csv and png will be generated
'''
class PathGenerator:
    def __init__(self):
        self.positions=[]
        self.img=None

    def generate_points(self):
        positions=[]
        xu=0
        yu=0
        #open layout
        img= cv2.imread("layout.png")
        cv2.imshow('layout',img)
        cv2.waitKey(0) #required for opencv rendering
        #detect corner to generate relative coords
        res=pyautogui.locateOnScreen('plot_edge.png')
        if res is None:
            print(" layout detection failed")
        else:
            xu,yu,xl,yl=res
            print(xu)
            print(yu)

        time.sleep(1) #setup time

        while True:
            res = pyautogui.locateOnScreen('plot_edge.png')
            if res is None:
                print("detection failed")
            else:
                xu, yu, xl, yl = res
                xl=xu+750
                yl=yu+477
            pos= pyautogui.position();
            #normal points
            if pos.x >xu and pos.x < xl and pos.y>yu and pos.y<yl:
                positions.append([pos.x-xu,pos.y-yu])
            #far away -> stop
            elif (pos.x<xu-100 or pos.x>xl+100) or (pos.y<yu-100 or pos.y>yl+100):
                print(pos.x)
                print(pos.y)
                print('break')
                break
            else:
                x=pos.x
                y=pos.y
                x=max(min(xl,x),xu)
                y=max(min(yl,y),yu)
                positions.append([x-xu,y-yu])

            print(positions[-1])
            #vis new waypoint
            cv2.circle(img, (positions[-1][0], positions[-1][1]), 5, (0, 0, 255), -1)
            if (len(positions)>=2):
                cv2.line(img, (positions[-2][0], positions[-2][1]), (positions[-1][0], positions[-1][1]), (0, 0, 255), 2)
            cv2.destroyAllWindows()
            cv2.imshow('layout', img)
            cv2.waitKey(0)  # required for opencv rendering
        self.positions=positions
        self.image=img



    #TODO: gaussion noise on trail
    #TODO: divide long lines in subpoints

    def get_csv_and_png(self,filename=None,png=True):
        positions=self.positions.copy()
        vel = 110  # cm/s velocity
        if filename is None:
            filename='test'

        cv2.imwrite(filename+'.png',self.image)
        #determine timestamps
        p=np.array(self.positions)
        p_x=p[:,0]
        p_y=p[:,1]
        d_x=np.ediff1d(p_x)
        d_y=np.ediff1d(p_y)
        d=np.sqrt(np.power(d_x,2)+np.power(d_y,2))

        with open(filename+'.csv', 'w', newline='') as outfile:
            writer = csv.writer(outfile, delimiter=',')
            writer.writerow(["x_coord","y_coord","rel_time"])
            for i in range(1,len(positions)):
                writer.writerow([positions[i][0], positions[i][1], np.sum(d[:i-1])/vel])


if __name__=='__main__':
    pg = PathGenerator()
    pg.generate_points()
    filename='testnew'
    png=True
    pg.get_csv_and_png(filename, png)


'''
def main(filename,png=True):
    pg=PathGenerator()
    pg.generate_points()
    pg.get_csv_and_png(filename,png)
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-fn', '--filename', type=str, required=True, help="filename")
    parser.add_argument('-png','--png',type=bool,required=False,help='png generated?')
    args = parser.parse_args()

    main(**vars(args))
'''
