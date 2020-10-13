import cv2
import matplotlib.pyplot as plt
import scipy.ndimage.filters as filter
import numpy as np
from help_module.csv_helper import read_data
import matplotlib.image as image

'''
this is a file to experiment with img processing, therefore it is quite unreadable
'''

#353
num=450

data=read_data('files/sensor_data_episode_20190221-143435_0.csv',0,502) #manually selected empty frames of this episode
im1=data[num][0].reshape((24,32)).astype(np.uint8)
im1_b=filter.gaussian_filter(im1,1).astype(np.uint8)

#work around issue of converting python array to opencv img
image.imsave('files/name.png', im1_b)
img=cv2.imread('files/name.png')
print(np.ndim(img))
img=cv2.resize(img,None,fx=10,fy=10)

gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

plt.hist(gray.ravel(),256,[0,256])
plt.show()
####
#OTSU takes first peaks (as i currently understand it) -> highest peak is what we want
#gray=255-gray;
#OTSUU
#ret,thresh = cv2.threshold(gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)


#basically this filter will make all 'bright' objects smaller, eliminating noise and improving accuracy
#thresh=255-thresh
#thresh=cv2.erode(thresh,None,iterations=10)
#####
#OWN DEFINED
hist=np.histogram(gray,50);
thresh_val=hist[1][-5]
ret,thresh=cv2.threshold(gray,thresh_val,255,cv2.THRESH_BINARY)
print('ret=' + str(ret))
#IMPORTANT! some versions of opencv have 3 output values for this findContours
contours,hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

cv2.drawContours(img,contours,-1,100,3)
print('num of contours='+str(len(contours)))
for c in contours:
    # calculate moments for each contour
    M = cv2.moments(c)
    # calculate x,y coordinate of center
    if M["m00"] != 0:
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
    else:
        cX, cY = 0, 0
    print(cX)
    print(cY)
    cv2.circle(img, (cX, cY), 5, (255,255,0), -1)
# display the image
cv2.imshow("Image", img)
cv2.waitKey(0)

#TODO
#determine gaussian blur params
#TODO
#dig into all possible morphological TF's to determine the best options
#TODO
#change the dynamic otsu threshold to keep hottest pixels
#=> hist shows that usually there are 2 background colors which are dominant -> make them one!
