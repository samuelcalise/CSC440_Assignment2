"""
Name: Sam Calise and Nick Robillard
"""

import math
import sys
from typing import List
from typing import Tuple

EPSILON = sys.float_info.epsilon
Point = Tuple[int, int]


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


def base_case_hull(points: List[Point]) -> List[Point]:
    """ Base case of the recursive algorithm.
    """
    if len(points) < 4:
        return points

    # Sorting the provided points
    points.sort()

    return [points[0], points[-1]]


def compute_hull(points: List[Point]) -> List[Point]:
    """
    Given a list of points, computes the convex hull around those points
    and returns only the points that are on the hull.
    """
    # TODO: Implement a correct computation of the convex hull
    #  using the divide-and-conquer algorithm
    # TODO: Document your Initialization, Maintenance and Termination invariants.
    sort_clockwise(points)

    return divide_n_conquer_algo(points)


def divide_n_conquer_algo(points: List[Point]) -> List[Point]:
    # Implementing base case of left and right hull lists
    if len(points) <= 3:
        return base_case_hull(points)

    # Divide master lst `points` into required divided lists
    # dependent on the sorted midpoint
    my_mid_point = len(points) // 2
    left_hull_list = points[:my_mid_point]
    right_hull_list = points[my_mid_point:]

    left_hull_list = divide_n_conquer_algo(left_hull_list)
    right_hull_list = divide_n_conquer_algo(right_hull_list)

    finalized_list = combine_hull_lists(left_hull_list, right_hull_list)

    return finalized_list

def combine_hull_lists(left_hull: List[Point], right_hull: List[Point]) -> List[Point]:
    # One time lambda function to get the highest point from
    # the left and the lowest point in the right list
    highest_point = max(left_hull, key=lambda p: p[1])
    lowest_point = min(right_hull, key=lambda p: p[1])

    UPPER_tangent = get_tangent_value(left_hull, highest_point, lowest_point, compare=lambda a, b: a < b)
    LOWER_tangent = get_tangent_value(right_hull, highest_point, lowest_point, compare=lambda a, b: a > b)

    # Ensure the tangent points are within their respective hull lists
    if UPPER_tangent not in left_hull:
        return right_hull
    if LOWER_tangent not in right_hull:
        return left_hull

    # Pointing out the 4 corners within the list of points
    UPPER_left_idx = left_hull.index(UPPER_tangent)
    UPPER_right_idx = right_hull.index(UPPER_tangent)

    LOWER_left_idx = left_hull.index(LOWER_tangent)
    LOWER_right_idx = right_hull.index(LOWER_tangent)

    combined_lists = (left_hull[:UPPER_left_idx] +
                      right_hull[UPPER_right_idx:LOWER_right_idx + 1] +
                      left_hull[LOWER_left_idx:])

    return combined_lists


def get_tangent_value(hull: List[Point], highest_p: Point, lowest_p: Point, compare) -> Point:
    for some_element in range(len(hull)):
        first_point = hull[some_element]
        second_point = hull[(some_element + 1) % len(hull)]

        if compare(triangle_area(highest_p, lowest_p, first_point), 0) and \
                compare(triangle_area(highest_p, lowest_p, second_point), 0) and \
                is_counter_clockwise(highest_p, lowest_p, first_point) and \
                is_counter_clockwise(highest_p, lowest_p, second_point):
            return first_point
