from cv2 import *

# initialize the camera
cam = VideoCapture(1)   # 0 -> index of camera
s, img = cam.read()

imwrite("filename.jpg",img)