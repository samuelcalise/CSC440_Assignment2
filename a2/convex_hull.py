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


def left_check(a: Point, b: Point, c: Point) -> bool:
    "Checks if c is left of the cross product of a and b"
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]) > 0


def base_case_hull(points: List[Point]) -> List[Point]:
    """ Base case of the recursive algorithm.
    """
    length = len(points)
    if length <= 3:
        return points

    start = min(points, key=lambda p: p[0])  # Find the leftmost point
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

    sort_clockwise(hull)

    return hull



def compute_hull(points: List[Point]) -> List[Point]:
    # Sort the points clockwise
    # sort_clockwise(points)

    points.sort()

    if len(points) <= 6:
        return base_case_hull(points)

    middle = len(points) // 2
    left = points[:middle]
    right = points[middle:]

    left_hull = compute_hull(left)
    right_hull = compute_hull(right)


    UPPER_left, UPPER_right = find_UPPER_tangent(left_hull, right_hull)

    LOWER_left, LOWER_right = find_LOWER_tangent(left_hull, right_hull)

    merged = merge_convex_hulls(UPPER_left, UPPER_right, LOWER_left, LOWER_right, left_hull, right_hull)


    return merged


def find_UPPER_tangent(left_hull, right_hull):
    """
    Finds the upper tangent between the left and right hulls.
    """
    i = left_hull.index(max(left_hull))
    j = right_hull.index(min(right_hull))

    while True:

        if is_counter_clockwise(left_hull[i], right_hull[j], right_hull[(j+1)% len(right_hull)]):
            j = (j + 1) % len(right_hull)
        elif is_clockwise(right_hull[j], left_hull[i], left_hull[(i - 1)% len(left_hull)]):
            i = (i - 1) % len(left_hull)
        else:
            break

    return left_hull[i], right_hull[j]


def find_LOWER_tangent(left_hull, right_hull):
    """
    Finds the lower tangent between the left and right hulls.
    """
    i = left_hull.index(max(left_hull))
    j = right_hull.index(min(right_hull))

    while True:
        next_i = (i + 1) % len(left_hull)
        if is_counter_clockwise(right_hull[j], left_hull[i], left_hull[next_i]):
            i = next_i
        elif is_clockwise(left_hull[i], right_hull[j], right_hull[(j - 1) % len(right_hull)]):
            j = (j - 1) % len(right_hull)
        else:
            break

    return left_hull[i], right_hull[j]

def merge_convex_hulls(UPPER_left, UPPER_right, LOWER_left, LOWER_right, left_hull, right_hull):
    newer_hull = []

    # Add points from the left hull
    index = left_hull.index(LOWER_left)
    while left_hull[index] != UPPER_left:
        newer_hull.append(left_hull[index])
        index = (index + 1) % len(left_hull)
    newer_hull.append(UPPER_left)


    # Add points from the right hull
    index = right_hull.index(UPPER_right)
    while right_hull[index] != LOWER_right:
        newer_hull.append(right_hull[index])
        index = (index + 1) % len(right_hull)
    newer_hull.append(LOWER_right)


    return newer_hull
