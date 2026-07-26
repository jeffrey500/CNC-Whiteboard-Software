import math
from pathlib import Path

import cv2
import numpy as np


# return the optimal order of paths
def greedy(path: list[list[tuple[float, float]]]):
    # Euclidean distance between two coordinates
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


def visualize_paths(paths, filename, svg: bool, height=1200, width=2030):
    # Create a blank white canvas matching the image dimensions
    canvas = np.ones((height, width, 3), dtype=np.uint8) * 255

    for path in paths:
        if len(path) > 1:
            # Generate a random dark color for each stroke to easily tell them apart
            color = tuple(np.random.randint(0, 150, 3).tolist())

            # OpenCV polylines requires coordinates as a numpy array of shape (N, 1, 2)
            pts = np.array(path, np.int32).reshape((-1, 1, 2))

            # Draw the continuous path
            cv2.polylines(canvas, [pts], isClosed=False, color=color, thickness=2)

            # draw the start points in red
            start_point = (int(path[0][0]), int(path[0][1]))
            cv2.circle(canvas, start_point, radius=3, color=(0, 0, 255), thickness=-1)

    filename = Path(filename).stem

    if svg:
        cv2.imwrite(Path(__file__).parent.parent / "data" / "svg_render" / f"{str(filename)}.png", canvas)
    else:
        cv2.imwrite(Path(__file__).parent.parent / "data" / "image_render" / f"{str(filename)}.png", canvas)


def generate_gcode_from_path(paths, svg: bool, feedrate=30000, output_path_name="commands", offset=(60, -15)):
    start = start_gcode(feedrate)
    end = end_gcode()

    if svg:
        output_path = Path(__file__).parent.parent / "data" / "svg_gcode_output" / f"{output_path_name}.gcode"
    else:
        output_path = Path(__file__).parent.parent / "data" / "image_gcode_output" / f"{output_path_name}.gcode"

    with open(output_path, "w") as file:
        # start gcode
        for cmd in start:
            file.write(cmd + "\n")

        for path in paths:
            if len(path) > 1:
                first = path[0]

                # go to start of contour
                file.write(f"G0 X{round(first[0], 3) + offset[0]} Y{round(first[1], 3) + offset[1]}" + "\n")

                # put marker down
                file.write("M3 S1000;put marker down\n")
                file.write("G4 P0.2\n")

                # draw contour
                for i in range(1, len(path)):
                    point = path[i]
                    file.write(f"G1 X{round(point[0], 3) + offset[0]} Y{round(point[1], 3) + offset[1]}" + "\n")

                # lift marker up
                file.write("M5; lift marker up\n")
                file.write("G4 P0.08\n")

        # end gcode
        for cmd in end:
            file.write(cmd + "\n")

    return output_path


# initial gcode
def start_gcode(feed_rate: int):
    return ["$H ; Home all axes (move to limit switches)",
            "$1=255 ; lock motors",
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
            "M5; lift up pen",
            "G4 P0.08",
            "G0X0Y0",
            ";ug$1=0 ; unlock motors", ]
