import cv2
from datetime import time, timedelta, datetime, date
import math

video_location = 'D:/VOP_scenarios/scenarios/videos_0905/gilles_video.mp4'

frame_location = 'D:/test/'
save_location = 'D:/VOP_scenarios/scenarios/2_personen/rgb_frames/'

video_start = datetime.combine(date.today(), time(hour=14, minute=3, second=34))
video_stop = datetime.combine(date.today(), time(hour=15, minute=44, second=28))

scene_start = datetime.combine(date.today(), time(hour=15, minute=0, second=0))
scene_stop = datetime.combine(date.today(), time(hour=15, minute=21, second=0))

fps = 28.86
frame_margin = 100


scene_start_frame = int((scene_start - video_start).seconds * fps - frame_margin)
scene_stop_frame = int((scene_stop - video_start).seconds * fps + frame_margin)
scene_frame_amount = scene_stop_frame - scene_start_frame

cap = cv2.VideoCapture(video_location)

i = 0
cap.set(1,scene_start_frame)

for i in range(scene_frame_amount // 2):
    _, _ = cap.read()
    ret, frame = cap.read()
    img_name = save_location + ('000000' + str(i))[-6:] + '.png'
    print(img_name)
    cv2.imwrite(img_name, frame)
    if ret == False:
        print('Doesn\'t work')
        break


cap.release()
cv2.destroyAllWindows()