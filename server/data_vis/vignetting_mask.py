import numpy as np
from help_module.csv_helper import read_data
from help_module.img_helper import convert_to_thermal_image
from help_module.flask_helper import serve_pil_image
import matplotlib.pyplot as plt
import scipy.ndimage.filters as filter

def clean_data(data):
    cleaned=[]
    for frame in data:
        if min(frame)>10 and max(frame) <50:
            cleaned.append(frame)
    print('total frames='+str(len(data))+',useful frames:'+str(len(cleaned)))
    return np.array(cleaned)

def generate_mask(data,max_corr=6):
    data=np.array(data)[:,0]
    data=clean_data(data)
    data.flatten()
    mean=np.mean(data,0)
    mask= mean- np.min(mean)
    max=np.max(mask)
    if max> max_corr:
        mask*=(max_corr/max)
    return mask

num =25
data=read_data('sensor_data_episode_20190221-143435_0.csv',0,502) #manually selected empty frames of this episode

#VIGNETTING
mask=generate_mask(data[443:502])
print(mask)
print(data[num][1])
im1=data[num][0].reshape((24,32))
im1_b=filter.gaussian_filter(im1,1)
im2=(data[num][0]-mask).reshape((24,32))
im2_b=filter.gaussian_filter(im2,1)
print(im1)
#display both to compare them and find a frame with persons in it to apply the mask

plt.axis('scaled')
fig, axarr = plt.subplots(3, 2)
c = axarr[0,0].pcolor(im1)
axarr[0,0].set_title('raw data')
fig.colorbar(c, ax=axarr[0,0])

d = axarr[0,1].pcolor(im1_b)
axarr[0,1].set_title('raw data blurred')
fig.colorbar(d, ax=axarr[0,1])

f = axarr[1,1].pcolor(im2_b)
axarr[1,1].set_title('masked data blurred')
fig.colorbar(f, ax=axarr[1,1])

g = axarr[1,0].pcolor(im2)
axarr[1,0].set_title('masked data')
fig.colorbar(g, ax=axarr[1,0])
# plt.gca().set_aspect('equal', adjustable='box')



#EDGE DETECTION
print('start sobel')
im_bin= np.where(im1_b>28,1,0)
dx=filter.sobel(im2_b,0)
dy=filter.sobel(im2_b,1)
mag=np.hypot(dx,dy) #sqrt(x**2+y**2)
mag *=255/np.max(mag)
print('sobel finished')
mag.reshape((24,32))
axarr[2,0].pcolor(im_bin)
axarr[2,0].set_title(' 28deg splitted data')
axarr[2,1].pcolor(mag)
axarr[2,1].set_title('sobel on masked, blurred data')

plt.show()

