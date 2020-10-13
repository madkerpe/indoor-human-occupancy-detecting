import  math
def point_dist(p1, p2):
    f1 = math.pow(p1[0] - p2[0], 2)
    f2 = math.pow(p1[1] - p2[1], 2)

    return math.sqrt(f1 + f2)


def point_line_diff(line, point):
    x1 = line[0]
    y1 = line[1]
    x2 = line[2]
    y2 = line[3]

    x0 = point[0]
    y0 = point[1]

    top = abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1)
    bottom = math.sqrt(math.pow(y2 - y1, 2) + math.pow(x2 - x1, 2))

    return top/bottom