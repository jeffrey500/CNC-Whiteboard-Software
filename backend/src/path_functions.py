import math

import numpy as np

# return the optimal order of paths
def greedy(path: list[list[tuple[float, float]]]):

    #euclidean distance between two coordinates
    def distance(coord1, coord2):
        return math.sqrt(math.pow(coord1[0] - coord2[0], 2) + math.pow(coord1[1] - coord2[1], 2))

    output = [path[0]]
    last_path_end = path[0][-1]
    visited = np.zeros(len(path))
    visited[0] = 1
    paths_left = len(path) - 1

    while paths_left != 0:
        lowest_distance = float('inf')
        lowest_index = -1
        for i in range(len(path)):
            if visited[i] == 0:
                point_distance = distance(last_path_end, path[i][0])
                if point_distance < lowest_distance:
                    lowest_distance = point_distance
                    lowest_index = i
        output.append(path[lowest_index])
        last_path_end = path[lowest_index][-1]
        paths_left -= 1
        visited[lowest_index] = 1

    return output

def get_transformed_point(point: list[list[tuple[float, float]]], matrix: np.ndarray):
        vector_point = np.array([point[0], point[1], 1])

        transformed = matrix @ vector_point

        return transformed[:2]

def transform_path(path: list[list[tuple[float, float]]], matrix: np.ndarray):
    output = []

    for cont_path in path:
        np_points = np.array(cont_path)
        ones = np.ones((len(np_points), 1))
        np_points = np.hstack([np_points, ones])

        transformed_points = np_points @ matrix.T

        output.append(transformed_points[:, :2])

    return output

# initial gcode
def start_gcode(feed_rate: int):
    return [";$H ; Home all axes (move to limit switches)",
            ";$1=255 ; lock motors",
            "G28.1 ; set new home after homing",
            "G21 ; Set units to Millimeters",
            "G90 ; Set to Absolute Positioning",
            "G17 ; Select XY plane (standard for 2D plotting)",
            "; lift up pen",
            f"G94F{feed_rate} ; Set feed rate mode to \"units per minute\"",
            "; starting plotting"
            ]

# ending gcode
def end_gcode():
    return ["; finished plotting",
            "; lift up pen",
            "G0X0Y0",
            ";ug$1=0 ; unlock motors", ]