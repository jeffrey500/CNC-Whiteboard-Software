from svgpathtools import svg2paths, CubicBezier, QuadraticBezier, Arc
import numpy as np
import math

# return the optimal order of paths
def greedy(paths):

    def distance(coord1, coord2):
        return math.sqrt(math.pow(coord1[0] - coord2[0], 2) + math.pow(coord1[1] - coord2[1], 2))

    output = [paths[0]]
    last_path_end = paths[0][-1]
    visited = np.zeros(len(paths))
    visited[0] = 1
    paths_left = len(paths) - 1

    while paths_left != 0:
        lowest_distance = 100000
        lowest_index = -1
        for i in range(len(paths)):
            if visited[i] == 0:
                point_distance = distance(last_path_end, paths[i][0])
                if point_distance < lowest_distance:
                    lowest_distance = point_distance
                    lowest_index = i
        output.append(paths[lowest_index])
        last_path_end = paths[lowest_index][-1]
        paths_left -= 1
        visited[lowest_index] = 1

    return output

#return svg points and paths given the svg file path
def svg_to_paths(file_path: str, curve_resolution=0.3):

    def get_transform_matrix():


    #list of path objects, list of dictionaries of XML attributes
    paths, attributes = svg_to_paths(file_path)

    output_paths = []

    #loop through the continuous paths
    for path, attribute in zip(paths,attributes):

        path_matrix = get_transform_matrix

        output_path = []

        #loop through the segments within each path
        for segment in path:

            output_segment = []

            start_x = segment.start.real
            start_y = segment.start.imag

            end_x = segment.end.real
            end_y = segment.end.imag

            output_segment.append((start_x, start_y))

            #segments can be a line, CubicBezier, QuadraticBezier, or Arc
            if isinstance(segment, CubicBezier):

            elif isinstance(segment, QuadraticBezier):

            elif isinstance(segment, Arc):

            output_segment.append((end_x, end_y))

            output_path.append(output_segment)

        output_paths.append(output_path)

    return output_paths

#initial gcode
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

#ending gcode
def end_gcode():
    return ["; finished plotting",
            "; lift up pen",
            "G0X0Y0",
            ";ug$1=0 ; unlock motors",]

#generate gcode file
def generate_gcode_from_svg(file_path: str, matrix: np.ndarray, feedrate: int, resolution=1):
    start = start_gcode(feedrate)
    end = end_gcode()

    points = svg_to_points(file_path, resolution)

    scaled_points = scale_svg_points(points, matrix)

    paths = greedy(scaled_points)

    with open("./temp/commands.gcode", "w") as file:
        #start gcode
        for cmd in start:
            file.write(cmd + "\n")

        for path in paths:
            if len(path) > 1:
                first = path[0]

                #go to start of contour
                file.write(f"G0 X{round(first[0],3)} Y{round(first[1],3)}" + "\n")

                # put marker down
                file.write("M3 S1000;put marker down\n")
                file.write("G4 P0.2\n")

                #draw contour
                for i in range(1, len(path)):
                    point = path[i]
                    file.write(f"G1 X{round(point[0],3)} Y{round(point[1],3)}" + "\n")

                # lift marker up
                file.write("M5; lift marker up\n")
                file.write("G4 P0.08\n")

        #end gcode
        for cmd in end:
            file.write(cmd + "\n")

    return f"./temp/{file_path}.gcode"