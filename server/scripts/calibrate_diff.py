from PIL import Image, ImageDraw


def get_bounding_box(co, c_width=4):
    x1 = co[0] - c_width
    x2 = co[0] + c_width
    y1 = co[1] - c_width
    y2 = co[1] + c_width

    return [x1, y1, x2, y2]

def invert(co1, co2):
    width = 750
    height = 477
    n_co1 = (width - co1[1], height - co1[0])
    n_co2 = (width - co2[1], height - co2[0])
    return n_co1, n_co2

cal_points = [((370,407),(320,380),(270,357),(240,335),(200,311),(160,237),(110,259),(150,378),(200,355),(220,346),(260,328),(330,295)),
              ((360,233),(299,190),(270,169),(240,147),(201,118),(130,67),(131,224),(213,167),(284,116),(348,67))]
meas_points = [((355,404),(324,383),(273,355),(230,325),(188,290),(145,270),(112,250),(142,353),(189,348),(200,336),(254,327),(333,295)),
               ((360,253),(287,203),(263,175),(259,147),(188,115),(151,93),(110,207),(191,163),(282,122),(338,82))]

diff_colors = [(255, 0, 0), (255, 255, 0)]

img_file = '../../GUI/static/Img/layout.png'

img = Image.open(img_file)

d = ImageDraw.Draw(img)

for cal_points_set, meas_points_set, color in zip(cal_points, meas_points, diff_colors):
    for cal_point, meas_point in zip(cal_points_set, meas_points_set):
        print('=============')
        rev_cal_point = (cal_point[1], cal_point[0])
        rev_meas_point = (meas_point[1], meas_point[0])
        box1 = get_bounding_box(rev_cal_point)
        d.ellipse(box1, fill=(0,0,0))
        box2 = get_bounding_box(rev_meas_point)
        d.ellipse(box2, fill=color)
        d.line([rev_cal_point, rev_meas_point],width=2, fill=(0,0,0))

img.save('calibrate_point_diff.png')