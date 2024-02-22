"""
Names: Sam Calise and Nick Robillard

Invariant Documentation
• Invariant: A statement that can be checked at any point in time. It should
relate to how the algorithm makes progress.

The invariant in this program is based on points given by the user GUI and
determined based on the length of points `n.` If n <= 6, our base_case_hull is
invoked and quickly completes the solution of any points less than or equal to 6.
However, based on the GUI, if the length of points is greater than 6, our divide
and conquer compute_hull algorithm of O(n logn) is invoked to complete the solution
of a convex hull that is based on `n` as the number of points that is greater than
six will be completed with the expected result visually through the GUI.

• Initialization: how is the problem set up

Our Initialization invariant in this program is running compute_hull and determining
whether, based on the length of the point list, it is greater than six or less than or
equal to 6. The initial step determines whether a divide-and-conquer or base_case hull
solution is needed to complete the convex hull solution.


• Maintenance: how do I know I’m making progress?

The Maintenance invariant in the program maintains our collection of clockwise points
to complete the divide-and-conquer algorithm to solve the convex hull. Also, get the
upper and lower tangents from the left and right hull lists. Finally, the merge algorithm
can traverse clockwise through the left and right hull lists through the upper and lower
tangent indexes in the lists.


• Termination: how do I know I’m done?

The Termination invariant in this program is based on the merge list successfully
iterating through the two left and right hull lists in clockwise order. Also, the
base_case_hull is able to return the points when the length of the list is less than
or equal to 6 and returning the points is clockwise order.

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


"""
Function: left_check -> Returns bool

When implementing our base case for the convex hull, 
the function is intended to help complete the smaller 
divided sub-lists from the pointers gathered from the GUI.
"""


def left_check(a: Point, b: Point, c: Point) -> bool:
    "Checks if c is left of the cross product of a and b"
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]) > 0


"""
Function: base_case_hull -> Return List[Point]

The purpose of this function is to brute force the smaller 
subset of points from an initial list. After the while loop 
completes the computation of points from compute_hull, the 
points are sorted by the helper function sort_clockwise. 
When the list of points is passed to this function, the runtime 
is still O(n logn). The reasoning behind the runtime complexity 
is due to the List[Point]'s being sorted ahead of time before 
entering the base case function. This does not hinder the 
runtime complexity of our divide-and-conquer algorithm.
"""


def base_case_hull(points: List[Point]) -> List[Point]:
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


"""
Function: compute_hull -> Returns List[Point]

The compute_hull function will return the recursive operations 
of solving the convex hull based on various sizes gathered from 
user input. The points are sorted based on the elements 'x' 
values from user input and then split into two subsets, 
performing the divide and conquer algorithm to solve and display 
the expected convex hull. After the recursive steps are completed 
by on the size of the list of points, the function will return 
the completed List[Points] and draw the expected output in 
clockwise order.
"""


def compute_hull(points: List[Point]) -> List[Point]:
    # Sorting values based on x data field of tuple
    points.sort()

    if len(points) <= 6:
        return base_case_hull(points)

    # Getting the mid-point of the initial list
    middle = len(points) // 2

    # Divide the initial list into 2 sub lists
    left = points[:middle]
    right = points[middle:]

    # Preforming the divide and conquer algorithm
    left_hull = compute_hull(left)
    right_hull = compute_hull(right)

    # Getting the upper and lower tangents from the 2 sub lists
    UPPER_left, UPPER_right = find_UPPER_tangent(left_hull, right_hull)
    LOWER_left, LOWER_right = find_LOWER_tangent(left_hull, right_hull)

    # Preforming the merge of the two lists in clockwise order
    merged = merge_convex_hulls(UPPER_left, UPPER_right, LOWER_left, LOWER_right, left_hull, right_hull)

    # Completed divide and conquer solution
    return merged


"""
Function: find_UPPER_tangent -> Returns Point[index], Point[index]

When computing the upper tangent of the given lists, we traverse
clockwise and counterclockwise steps until the program reaches the 
upper most 2 points of the left and right hull lists
"""


def find_UPPER_tangent(left_hull, right_hull):
    i = left_hull.index(max(left_hull))
    j = right_hull.index(min(right_hull))

    while True:
        # Looking for the upper right most tangent point
        if is_counter_clockwise(left_hull[i], right_hull[j], right_hull[(j + 1) % len(right_hull)]):
            j = (j + 1) % len(right_hull)

        # Looking for the upper left most tangent point
        elif is_clockwise(right_hull[j], left_hull[i], left_hull[(i - 1) % len(left_hull)]):
            i = (i - 1) % len(left_hull)
        else:
            break

    # Returning the tangent points
    return left_hull[i], right_hull[j]


"""
Function: find_LOWER_tangent -> Returns Point[index], Point[index]

When computing the upper tangent of the given lists, we are traverse
clockwise and counterclockwise steps until the program reaches the 
lower most 2 points of the left and right hull lists
"""


def find_LOWER_tangent(left_hull, right_hull):
    """
    Finds the lower tangent between the left and right hulls.
    """
    i = left_hull.index(max(left_hull))
    j = right_hull.index(min(right_hull))

    while True:
        next_i = (i + 1) % len(left_hull)
        # Looking for the lower left most tangent point
        if is_counter_clockwise(right_hull[j], left_hull[i], left_hull[next_i]):
            i = next_i

        # Looking for the lower right most tangent point
        elif is_clockwise(left_hull[i], right_hull[j], right_hull[(j - 1) % len(right_hull)]):
            j = (j - 1) % len(right_hull)
        else:
            break

    # Returning the tangent points
    return left_hull[i], right_hull[j]


"""
Function: merge_convex_hull -> Returns List[Points]

This function aims to iterate through the left and right 
hulls based on the upper and the lower tangent points to 
merge into a complete convex hull. The two while loops 
operate clockwise to merge the points into one ultimate 
convex hull, providing the correct solution to completing 
the convex hull.
"""


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

    # Returning the completed merged hull solution
    return newer_hull
