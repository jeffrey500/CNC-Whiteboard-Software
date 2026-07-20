import math
from pathlib import Path

from svgpathtools import svg2paths, Line
from path_functions import greedy, get_transformed_point, transform_path, start_gcode, end_gcode
import numpy as np

IDENTITY_MATRIX = np.array([[1,0,0], [0,1,0], [0,0,1]])

# return svg points and paths given the svg file path
def svg_to_paths(file_path: str, curve_resolution=0.3):
    # returns a np matrix for the svg code line
    def get_transform_matrix(str):
        if 'matrix' not in str:
            return np.eye(3)

        # remove "matrix(" and the ")" at the end
        str = str[7:-1]

        str = str.replace(",", " ")

        nums = str.split(" ")

        vals = []

        for val in nums:
            vals.append(float(val))

        return np.array([
            [vals[0], vals[2], vals[4]],
            [vals[1], vals[3], vals[5]],
            [0, 0, 1]
        ])

    # list of path objects, list of dictionaries of XML attributes
    paths, attributes = svg2paths(file_path)

    output_paths = []

    # loop through the continuous paths
    for path, attribute in zip(paths, attributes):

        path_matrix = get_transform_matrix(attribute.get("transform", ""))

        output_path = []

        # loop through the segments within each path
        for segment in path:

            output_segment = []

            if not math.isnan(segment.start.real) and not math.isnan(segment.start.imag):
                output_segment.append(get_transformed_point((segment.start.real, segment.start.imag), path_matrix))

            # segments can be a line, CubicBezier, QuadraticBezier, or Arc. Sample complex curve using parameters
            if isinstance(segment, Line):
                if not math.isnan(segment.end.real) and not math.isnan(segment.end.imag):
                    output_segment.append(get_transformed_point((segment.end.real, segment.end.imag), path_matrix))

            else:
                num_samples = max(1, int(segment.length() * curve_resolution))

                for i in range(1, num_samples + 1):
                    t = i / num_samples

                    try:
                        point = segment.point(t)
                        if not math.isnan(point.real) and not math.isnan(point.imag):
                            output_segment.append(get_transformed_point((point.real, point.imag), path_matrix))

                    # skip divide by zero rounding error
                    except ValueError:
                        pass

            output_path.extend(output_segment)

        output_paths.append(output_path)

    return greedy(output_paths)

# generate gcode file
def generate_gcode_from_svg(file_path: str, feedrate: int, matrix = IDENTITY_MATRIX, output_path_name="commands", resolution=0.03):
    start = start_gcode(feedrate)
    end = end_gcode()

    path = svg_to_paths(file_path, resolution)

    transformed_path = transform_path(path, matrix)

    output_path = Path(__file__).parent.parent / "data" / "svg_gcode_output" / f"{output_path_name}.gcode"

    with open(output_path, "w") as file:
        # start gcode
        for cmd in start:
            file.write(cmd + "\n")

        for path in transformed_path:
            if len(path) > 1:
                first = path[0]

                # go to start of contour
                file.write(f"G0 X{round(first[0], 3)} Y{round(first[1], 3)}" + "\n")

                # put marker down
                file.write("M3 S1000;put marker down\n")
                file.write("G4 P0.2\n")

                # draw contour
                for i in range(1, len(path)):
                    point = path[i]
                    file.write(f"G1 X{round(point[0], 3)} Y{round(point[1], 3)}" + "\n")

                # lift marker up
                file.write("M5; lift marker up\n")
                file.write("G4 P0.08\n")

        # end gcode
        for cmd in end:
            file.write(cmd + "\n")

    return f"backend/data/svg_gcode_output/{output_path_name}.gcode"