import numpy as np
from PIL import Image
import math
from scipy.interpolate import griddata


scale_factor = 20
width = 32
height = 24

points = [(i % width, math.floor(i / width)) for i in range(0, width * height)]


red_or = np.random.randint(0, 255, (width * height))

grid_x, grid_y = np.mgrid[0:width - 1:(width * scale_factor)*1j, 0:height - 1:(height * scale_factor)*1j]

bicubic = griddata(points, red_or, (grid_x, grid_y), method='cubic')
red = np.interp(bicubic, (bicubic.min(), bicubic.max()), (0, 255))


# red = np.repeat(red, scale_factor, axis=0)
# red = np.repeat(red, scale_factor, axis=1)

green = np.zeros((width * scale_factor, height*scale_factor))
blue = 255 - red

rgb_image = np.zeros((width * scale_factor, height * scale_factor, 3))

rgb_image[..., 0] = red
rgb_image[..., 1] = green
rgb_image[..., 2] = blue


im = Image.fromarray(rgb_image.astype('uint8'))
im.save('test_np_scipy.png')

new_red_points = np.reshape(red_or, (width, height))
new_green_points = np.zeros((width, height))
new_blue_points = 1 - new_red_points

rgb_image = np.zeros((width, height, 3))

rgb_image[..., 0] = new_red_points
rgb_image[..., 1] = new_green_points
rgb_image[..., 2] = new_blue_points

im = Image.fromarray(rgb_image.astype('uint8'))
im = im.resize((width * scale_factor, height * scale_factor), resample=Image.BICUBIC)
im.save('test_np_pil.png')