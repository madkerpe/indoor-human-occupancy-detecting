from PIL import Image, ImageDraw
from scipy.interpolate import griddata
import numpy as np
import io
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import scipy.ndimage.filters as fil
from datetime import datetime
import time
from help_module.csv_helper import read_data
from help_module.img_processing_helper import ImageProcessor
import base64
import math

def raw_color_plot(pixels, to_pil=True):
    fig = Figure()
    ax0 = fig.add_subplot(1,1,1)
    img_ar = np.array(pixels).reshape((24, 32))

    c = ax0.pcolor(img_ar)
    fig.colorbar(c, ax=ax0)

    ax0.axis('equal')

    if to_pil:
        return plt_fig_to_PIL(fig)
    else:
        return fig


def blur_color_plot(pixels, to_pil=True):
    fig = Figure()
    ax0 = fig.add_subplot(1, 1, 1)
    img_ar = np.array(pixels).reshape((24, 32))
    result = fil.gaussian_filter(img_ar, 1)

    c = ax0.pcolor(result)
    fig.colorbar(c, ax=ax0)

    ax0.axis('equal')

    if to_pil:
        return plt_fig_to_PIL(fig)
    else:
        return fig

def hist_plot(data, blur=True, to_pil=True):
    fig = Figure()
    ax0 = fig.add_subplot(1, 1, 1)
    # img_ar = np.array(pixels).reshape((24, 32))
    # if blur:
    #     img_ar = fil.gaussian_filter(img_ar, 1)

    # data = img_ar.reshape((1, -1)).ravel()

    ax0.hist(data, bins=20)

    if to_pil:
        return plt_fig_to_PIL(fig)
    else:
        return fig

def processed_color_plot(pixels,to_pil=True,thresh_method=None, mtplotlib=False):
    '''
    this function processes a raw image
    :param pixels: raw sensor data
    :param to_pil:
    :param thresh_method: which method to use for processing (in Img_processor class)
    :return: a figure on which all objects have a centroid and a contour
    '''
    processor=ImageProcessor()
    if thresh_method:
        processor.set_treshold_method(thresh_method)
    processor.process(pixels)
    data=processor.plot_frame()
    if mtplotlib:
        fig = Figure()
        ax0 = fig.add_subplot(1, 1, 1)
        ax0.imshow(data) #add this to mirror ,origin="lower"
        if to_pil:
            return plt_fig_to_PIL(fig)
        else:
            return fig
    else:
        return Image.fromarray(data, 'RGB') #already rescaled in the processing functions


def plt_fig_to_PIL(fig):
    """
    Converts matplotlib fig to PIL Image
    :param fig:
    :return:
    """
    buf = plt_fig_to_png_bytes(fig)
    img = Image.open(buf)
    return img


def plt_fig_to_png_bytes(fig):
    """
    Converts a matplotlib figure to a byte stream with png format
    :param fig:
    :return:
    """
    buf = io.BytesIO()
    FigureCanvas(fig).print_png(buf)
    buf.seek(0)
    return buf

def get_deltas(min_val, max_val, amount=8):
    """
    This function gives a list with values that are equal dist from each other to divide an image based on these values
    :param min_val:
    :param max_val:
    :param amount:
    :return:
    """
    delta = (max_val - min_val) / amount

    deltas = [min_val]

    for i in range(amount - 1):
        deltas.append(min_val + (i+1) * delta)

    deltas.append(float("inf"))

    return deltas

def get_deltas_img(img):
    """
    This function acts a wrapper around the get_deltas functions and just calculates the img max/min to give
    to the get_deltas. 0 is excluded from the min because nan gets converted to 0.
    :param img:
    :return:
    """
    try:
        min_img = np.min(img[img != 0])
    except:
        min_img = 0
    max_img = np.max(img)

    return get_deltas(min_img, max_img)

def get_fitted_img(img, max_size, return_mar=False):
    """
    Given a max size this gives a rescaled PIL image that fits in that size.
    :param img:
    :param max_size: (max_width, max_height)
    :param return_mar: boolean to indicate if the function has to return the margins.
    :return:
    """
    width, height = img.size
    ratio_x = max_size[0] / width
    ratio_y = max_size[1] / height
    ratio = max(ratio_x, ratio_y)

    n_width = int(ratio * width)
    n_height = int(ratio * height)
    img_res = img.resize((n_width, n_height))
    if not return_mar:
        return img_res
    else:
        return img_res, (int((max_size[0] - n_width)/2), int((max_size[1] - n_height)/2))

def grid_plot(images, locs, width, height, margin):
    """
    creates a grid of images

    :param images: assumed PIL images
    :param locs: (x,y) x and y are the two indices of were the image will be located
    :param width: height of one grid space
    :param height: width of one grid space
    :param margin: space between two grid spaces
    :return:
    """
    x_max_index = -1
    y_max_index = -1
    for loc in locs:
        x_max_index = loc[0] if loc[0] > x_max_index else x_max_index
        y_max_index = loc[1] if loc[1] > y_max_index else y_max_index

    img_width = (x_max_index + 1) * width + x_max_index * margin
    img_height = (y_max_index + 1) * height + y_max_index * margin

    grid_img = Image.new('RGB', (img_width, img_height))

    for index, img in enumerate(images):
        res_img, n_mar = get_fitted_img(img, (width, height), return_mar=True)

        x_start = locs[index][0] * (width + margin) + n_mar[0]
        y_start = locs[index][1] * (height + margin) + n_mar[1]

        grid_img.paste(res_img, (x_start, y_start))

    return grid_img


def get_thermal_color_tuples():
    return ((0, 0, 0), (68, 1, 84), (70, 50, 126), (54, 92, 141), (39, 127, 142), (31, 161, 135), (74, 193, 109),
              (160, 218, 57), (253, 231, 37))


def fast_thermal_image(pixels, scale=1, smooth=False, side=False, deltas=None, dim=(24, 32), as_numpy=False):
    """
    Return PIL image with a heatmap of the pixels, this should be faster then a matplotlib plot,
    There are only 9 different colorbrackets
    :param pixels: list with length 32x24 that contains the pixels from the sensor
    :param scale:
    :param smooth:
    :return:
    """
    img_ar = np.array(pixels)

    if img_ar.shape != dim:
        img_ar = img_ar.reshape(dim)

    if smooth:
        img_ar = fil.gaussian_filter(img_ar, 1)

    if dim != (24,32):
        scale = 1

    amount_delta = 8

    if deltas is None:
        deltas = get_deltas_img(img_ar)

    colors = get_thermal_color_tuples()

    if side:
        rgb_img = np.zeros((dim[0], dim[1] + 15, 3), dtype=np.uint8)
    else:
        rgb_img = np.zeros((dim[0], dim[1], 3), dtype=np.uint8)

    for color_range, color in zip(reversed(deltas), reversed(colors)):
        rgb_img[img_ar <= color_range] = np.array(color)

    rgb_img = rgb_img.repeat(scale, axis=0)
    rgb_img = rgb_img.repeat(scale, axis=1)

    if as_numpy:
        return rgb_img

    img = Image.fromarray(rgb_img, 'RGB')

    if not side:
        return img

    d = ImageDraw.Draw(img)

    x_sq_start = dim[1] * scale + 10
    x_sq_stop = x_sq_start + 50
    color_square_height = (dim[0] * scale) / (amount_delta + 1)

    for i in range(1, amount_delta):
        color_text = f'{deltas[i-1]}-{deltas[i]}'
        d.rectangle([(x_sq_start, i * color_square_height), (x_sq_stop, (i + 1) * color_square_height)], fill=colors[i])
        d.text((x_sq_stop + 10, i * color_square_height), color_text, fill=(255, 255, 255))

    color_text = f'-inf-{deltas[0]}'
    d.text((x_sq_stop + 10, 0), color_text, fill=(255, 255, 255))

    color_text = f'{deltas[-2]}-inf'
    d.rectangle(
        [(x_sq_start, amount_delta * color_square_height), (x_sq_stop, (amount_delta + 1) * color_square_height)],
        fill=colors[-1])
    d.text((x_sq_stop + 10, amount_delta * color_square_height), color_text, fill=(255, 255, 255))

    return img

def color_from_indices(img):
    colors = get_thermal_color_tuples()
    new_rgb = np.zeros((img.shape[0], img.shape[1], 3)).astype(np.uint8)
    for i in range(len(colors)):
        new_rgb[img == i] = np.array(colors[i])

    return new_rgb


def test_speed(img, function, dim):
    """
    Useful to test plot generation speed.
    :param img:
    :param function:
    :param dim:
    :return:
    """
    t0 = time.time()
    for _ in range(100):
        function(img, dim=dim)
    t1 = time.time()

    total = t1 - t0
    print(total)


def PIL_to_bytes(img):
    """
    Converts a PIL Image to jpeg byte stream
    :param img:
    :return:
    """
    img_io = io.BytesIO()
    img.save(img_io, 'JPEG', quality=70)
    img_io.seek(0)
    return img_io.getvalue()

def PIL_to_64(img):
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue())

    return img_str

def get_grid_form(amount):
    """
    Given an amount of items in the grid this gives the amount of rows and columns
    :param amount:
    :return:
    """
    plot_sizes = [1, 2, 4, 6, 9, 12, 15, 20]
    grid_sizes = [[1, 1], [2, 1], [2, 2], [3, 2], [3, 3], [3, 4], [3, 5], [4, 5]]
    grid = grid_sizes[0]

    for index in range(len(grid_sizes)):
        if amount <= plot_sizes[index]:
            grid = grid_sizes[index]
            break

    return grid

def combine_imgs(img_list, title=None):
    """
    Paste imgs on top of each other.
    :param img_list:
    :param title:
    :return:
    """
    min_width = float('inf')
    for img in img_list:
        if img.size[0] < min_width:
            min_width = img.size[0]

    rescaled_imgs = []
    total_height = 0
    for img in img_list:
        width, height = img.size
        factor = min_width / width
        new_height = int(factor * height)
        rescaled_imgs.append(img.resize((min_width, new_height)))
        total_height += new_height

    comp = Image.new('RGB', (min_width, total_height))
    current_height = 0

    for img in rescaled_imgs:
        comp.paste(img, (0,current_height))
        current_height += img.size[1]

    return comp


def get_bounding_box(co, c_width=4):
    x1 = co[0] - c_width
    x2 = co[0] + c_width
    y1 = co[1] - c_width
    y2 = co[1] + c_width

    return [x1, y1, x2, y2]


if __name__ == "__main__":
    for i in range(9):
        print(f'{i}: {get_grid_form(i)}')