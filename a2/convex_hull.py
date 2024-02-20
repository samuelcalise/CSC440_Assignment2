import math
import sys
from typing import List
from typing import Tuple
from functools import cmp_to_key

EPSILON = sys.float_info.epsilon
Point = Tuple[int, int]

mid = [0, 0]

def y_intercept(p1: Point, p2: Point, x: int) -> float:
    """
    Given two points, p1 and p2, an x coordinate from a vertical line,
    compute and return the y-intercept of the line segment p1->p2
    with the vertical line passing through x.
    """
    x1, y1 = p1
    x2, y2 = p2
    slope = (y2 - y1) / (x2 - x1)
    return y1 + (x - x1) * slope


def triangle_area(a: Point, b: Point, c: Point) -> float:
    """
    Given three points a,b,c,
    computes and returns the area defined by the triangle a,b,c.
    Note that this area will be negative if a,b,c represents a clockwise sequence,
    positive if it is counter-clockwise,
    and zero if the points are collinear.
    """
    ax, ay = a
    bx, by = b
    cx, cy = c
    return ((cx - bx) * (by - ay) - (bx - ax) * (cy - by)) / 2


def is_clockwise(a: Point, b: Point, c: Point) -> bool:
    """
    Given three points a,b,c,
    returns True if and only if a,b,c represents a clockwise sequence
    (subject to floating-point precision)
    """
    return triangle_area(a, b, c) < -EPSILON


def is_counter_clockwise(a: Point, b: Point, c: Point) -> bool:
    """
    Given three points a,b,c,
    returns True if and only if a,b,c represents a counter-clockwise sequence
    (subject to floating-point precision)
    """
    return triangle_area(a, b, c) > EPSILON

def collinear(a: Point, b: Point, c: Point) -> bool:
    """
    Given three points a,b,c,
    returns True if and only if a,b,c are collinear
    (subject to floating-point precision)
    """
    return abs(triangle_area(a, b, c)) <= EPSILON


def sort_clockwise(points: List[Point]):
    """
    Sorts `points` by ascending clockwise angle from +x about the centroid,
    breaking ties first by ascending x value and then by ascending y value.

    The order of equal points is not modified

    Note: This function modifies its argument
    """
    # Trivial cases don't need sorting, and this dodges divide-by-zero errors
    if len(points) < 2:
        return

    # Compute the centroid
    centroid_x = sum(p[0] for p in points) / len(points)
    centroid_y = sum(p[1] for p in points) / len(points)

    # Sort by ascending clockwise angle from +x, breaking ties with ^x then ^y
    def sort_key(point: Point):
        angle = math.atan2(point[1] - centroid_y, point[0] - centroid_x)
        normalized_angle = (angle + math.tau) % math.tau
        return normalized_angle, point[0], point[1]

    # Sort the points
    points.sort(key=sort_key)


# Checks whether the line is crossing the polygon
def orientation(a, b, c):
    res = (b[1]-a[1]) * (c[0]-b[0]) - (c[1]-b[1]) * (b[0]-a[0])
    if res == 0:
        return 0
    if res > 0:
        return 1
    return -1

# determines the quadrant of a point
def quad(p):
    if p[0] >= 0 and p[1] >= 0:
        return 1
    if p[0] <= 0 and p[1] >= 0:
        return 2
    if p[0] <= 0 and p[1] <= 0:
        return 3
    return 4

# compare function for sorting
def compare(p1, q1):
    p = [p1[0] - mid[0], p1[1] - mid[1]]
    q = [q1[0] - mid[0], q1[1] - mid[1]]
    one = quad(p)
    two = quad(q)

    if one != two:
        if one < two:
            return -1
        return 1
    if p[1] * q[0] < q[1] * p[0]:
        return -1
    return 1

def base_case_hull(points: List[Point]) -> List[Point]:
    """ Base case of the recursive algorithm.
    """

    global mid
    s = set()
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            x1, x2 = points[i][0], points[j][0]
            y1, y2 = points[i][1], points[j][1]
            a1, b1, c1 = y1 - y2, x2 - x1, x1 * y2 - y1 * x2
            pos, neg = 0, 0
            for k in range(len(points)):
                if (k == i) or (k == j) or (a1 * points[k][0] + b1 * points[k][1] + c1 <= 0):
                    neg += 1
                if (k == i) or (k == j) or (a1 * points[k][0] + b1 * points[k][1] + c1 >= 0):
                    pos += 1
            if pos == len(points) or neg == len(points):
                s.add(tuple(points[i]))
                s.add(tuple(points[j]))

    ret = list(s)

    # Sorting the points in the anti-clockwise order
    mid = [0, 0]
    n = len(ret)

    modified_points = []
    for point in ret:
        mid[0] += point[0]
        mid[1] += point[1]
        modified_points.append((point[0] * n, point[1] * n))

    ret = modified_points
    ret = sorted(ret, key=cmp_to_key(compare))
    for i in range(n):
        ret[i] = (ret[i][0] // n, ret[i][1] // n)

    return ret



def compute_hull(points: List[Point]) -> List[Point]:
    """
    Given a list of points, computes the convex hull around those points
    and returns only the points that are on the hull.
    """
    if len(points) <= 6:
        return base_case_hull(points)

    middle = len(points) // 2

    # sorts points
    sort_clockwise(points)

    left = points[:middle]
    right = points[middle:]

    left_hull = compute_hull(left)
    right_hull = compute_hull(right)

    merged_hull = merge_convex_hulls(left_hull, right_hull)

    return merged_hull


def find_upper_tangent(left_hull, right_hull):
    upper_a = max(left_hull, key=lambda p: p[0])
    upper_b = min(right_hull, key=lambda p: p[0])

    done = False
    while not done:
        done = True
        while orientation(right_hull[(right_hull.index(upper_b) + 1) % len(right_hull)], upper_a,
                          right_hull[right_hull.index(upper_b)]) <= 0:
            upper_b = right_hull[(right_hull.index(upper_b) + 1) % len(right_hull)]
        while orientation(left_hull[(left_hull.index(upper_a) - 1) % len(left_hull)], upper_b,
                          left_hull[left_hull.index(upper_a)]) >= 0:
            upper_a = left_hull[(left_hull.index(upper_a) - 1) % len(left_hull)]
            done = False
    return upper_a, upper_b


def find_lower_tangent(left_hull, right_hull):
    lower_a = min(left_hull, key=lambda p: p[0])
    lower_b = max(right_hull, key=lambda p: p[0])

    done = False
    while not done:
        done = True
        while orientation(right_hull[(right_hull.index(lower_b) - 1) % len(right_hull)], lower_a,
                          right_hull[right_hull.index(lower_b)]) >= 0:
            lower_b = right_hull[(right_hull.index(lower_b) - 1) % len(right_hull)]
        while orientation(left_hull[(left_hull.index(lower_a) + 1) % len(left_hull)], lower_b,
                          left_hull[left_hull.index(lower_a)]) <= 0:
            lower_a = left_hull[(left_hull.index(lower_a) + 1) % len(left_hull)]
            done = False
    return lower_a, lower_b


def merge_convex_hulls(left_hull, right_hull):
    upper_a, upper_b = find_upper_tangent(left_hull, right_hull)
    lower_a, lower_b = find_lower_tangent(left_hull, right_hull)

    merged_hull = []
    # Add the points from left hull from upper_a to lower_a
    idx = left_hull.index(upper_a)
    while idx != left_hull.index(lower_a):
        merged_hull.append(left_hull[idx])
        idx = (idx + 1) % len(left_hull)
    merged_hull.append(lower_a)

    # Add the points from right hull from lower_b to upper_b
    idx = right_hull.index(lower_b)
    while idx != right_hull.index(upper_b):
        merged_hull.append(right_hull[idx])
        idx = (idx + 1) % len(right_hull)
    merged_hull.append(upper_b)

    return merged_hull
