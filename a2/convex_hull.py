import math
import sys
from typing import List
from typing import Tuple

EPSILON = sys.float_info.epsilon
Point = Tuple[int, int]


def y_intercept(p1: Point, p2: Point, x: int) -> float:
    """
    Given two points, p1 and p2, an x coordinate from a vertical line,
    compute and return the the y-intercept of the line segment p1->p2
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
        return (normalized_angle, point[0], point[1])

    # Sort the points
    points.sort(key=sort_key)

def finding_starting_point(point_list: List[Point]) -> List[Point]:
    "Finds the starting point"
    leftmost = point_list[0]
    for point in point_list[1:]:
        if point[0] < leftmost[0] or (point[0] == leftmost[0] and point[1] < leftmost[1]):
            leftmost = point
    return leftmost

def left_check(a:Point, b:Point, c:Point) -> bool:
    "Checks if c is left of the cross product of a and b"
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]) > 0


def base_case_hull(points: List[Point]) -> List[Point]:
    """ Base case of the recursive algorithm.
    """
    length = len(points)
    if length <= 3:
        return points

    start = finding_starting_point(points)
    current = start
    hull = []

    while True:
        hull.append(current)
        next_point = points[0]  # Initialize with any point
        for point in points:
            if next_point == current:
                next_point = point
            elif left_check(current, next_point, point):
                next_point = point
        current = next_point
        if current == start:
            break

    return hull


def compute_hull(points: List[Point]) -> List[Point]:
    """
    Given a list of points, computes the convex hull around those points
    and returns only the points that are on the hull.
    """
    # sorts points
    sort_clockwise(points)

    if len(points) <= 6:
        return base_case_hull(points)

    middle = len(points) // 2

    left = points[:middle]
    right = points[middle:]

    print("left hull:",left,'\n',"RIght hul:",right)


    left_hull = compute_hull(left)
    right_hull = compute_hull(right)

    merged = merge_convex_hulls(left_hull, right_hull)

    return merged





def find_upper_tangent(left_hull, right_hull):
    """
    Finds the upper tangent between the left and right hulls.
    """
    n = len(left_hull)
    m = len(right_hull)
    i = 0
    j = 0

    while True:
        if is_counter_clockwise(right_hull[j], left_hull[i], left_hull[(i + 1) % n]):
            i = (i + 1) % n
        elif is_clockwise(left_hull[i], right_hull[j], right_hull[(j - 1) % m]):
            j = (j - 1) % m
        else:
            break

    return left_hull[i], right_hull[j]

def find_lower_tangent(left_hull, right_hull):
    """
    Finds the lower tangent between the left and right hulls.
    """
    n = len(left_hull)
    m = len(right_hull)
    i = 0
    j = 0

    while True:
        if is_clockwise(right_hull[(j - 1) % m], left_hull[i], left_hull[(i - 1) % n]):
            i = (i - 1) % n
        elif is_counter_clockwise(left_hull[i], right_hull[j], right_hull[(j + 1) % m]):
            j = (j + 1) % m
        else:
            break

    return left_hull[i], right_hull[j]


# keep in mind points are split horizontally for some reason so merging is weird
def merge_convex_hulls(left_hull, right_hull):
    """
    Merges the left and right convex hulls.
    """
    LLT, RLT = find_lower_tangent(left_hull, right_hull)
    LUT, RUT = find_upper_tangent(left_hull, right_hull)

    print('LLT: ', LLT)
    print('LUT: ', LUT)
    print('RLT: ', RLT)
    print('RUT: ', RUT)

    new_hull = []

    # Find the index of the right hull point with the same x-value as RLT
    idx_RLT = right_hull.index(RLT)

    # Add the points from RUT to RLT (inclusive)
    for i in range(idx_RLT, -1, -1):
        p = right_hull[i]
        if is_clockwise(RLT, LLT, p) and is_clockwise(RUT, LUT, p):
            new_hull.append(p)
        else:
            break

    # Find the index of the left hull point with the same x-value as LUT
    idx_LUT = left_hull.index(LUT)

    # Add the points from LLT to LUT (inclusive)
    for i in range(idx_LUT, len(left_hull)):
        p = left_hull[i]
        if is_clockwise(LLT, RLT, p) and is_clockwise(LUT, RUT, p):
            new_hull.append(p)
        else:
            break

    return new_hull

