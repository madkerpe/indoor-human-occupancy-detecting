import pytesseract
from PIL import Image
import cv2
import numpy as np
import pickle

img = cv2.imread('video_stuff/time_stamps/000000.png')

thresh_value = 230

new_width = 300
diff_x = 50
diff_y = 30
new_height = 90
img_width = 206
img_height = 31

ocr_prepare = np.zeros((new_height, new_width, 3))


video_location = '../../scenarios/videos_0905/gilles_video.mp4'

frame_location = 'D:/test/'

cap = cv2.VideoCapture(video_location)

ocr_results = []

i = 0
f = open('results.txt', 'w')
while cap.isOpened():
    ret, frame = cap.read()
    if ret == False:
        break
    if i % 100 == 0:
        print("============================")
        time = frame[0:190, 870:1280]
        # r = time[:, :, 0]
        # g = time[:, :, 1]
        # b = time[:, :, 2]
        # indices = np.logical_and(np.logical_and(r > thresh_value, g > thresh_value), b > thresh_value).astype(np.uint8) * 255
        # ocr_prepare[diff_y:diff_y + img_height, diff_x:diff_x + img_width] += time
        # cv2.imshow('image', ocr_prepare)
        # cv2.waitKey(0)
        result = pytesseract.image_to_string(time)
        print(f'{i}: {result}')
        f.write(result + '\n')

    i+=1

f.close()

cap.release()
cv2.destroyAllWindows()