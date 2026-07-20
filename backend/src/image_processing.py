import math
from pathlib import Path

import cv2
import numpy as np

from scipy.ndimage import convolve
from scipy.spatial import distance

from path_functions import generate_gcode_from_path

def generate_transformed_image(file_path: str, tag_length=85, tag_x_d=1860, tag_y_d=1030):
    #for april tags, the coordinates within the april tags are in the following order: top left, top right, bottom right, bottom left

    x_length, y_length = 2*tag_length + tag_x_d, 2*tag_length + tag_y_d

    #determine real-world positions of the whiteboard april tags
    real_corners = {}

    for i, (x, y) in enumerate([(0, 0), (tag_length + tag_x_d, 0), (0, tag_length + tag_y_d),
                                (tag_length + tag_x_d, tag_length + tag_y_d)]):
        real_corners[i + 1] = [(x, y), (x + tag_length, y), (x + tag_length, y + tag_length), (x, y + tag_length)]

    #load image as greyscale
    image = cv2.imread(file_path,0)

    #Load april tag dictionary, detector params, and detect the april tags
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_16h5)
    aruco_params = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_params)
    corners, ids, _ = detector.detectMarkers(image)

    #determine transformation matrix

    #build the real and image coordinate vectors
    real_cords,  image_cords = [], []

    if ids is not None:
        for marker_id, corner in zip(ids.flatten(), corners):
            real_cords.extend(real_corners[int(marker_id)])
            image_cords.extend(corner[0])

    real_cords = np.array(real_cords,dtype=np.float32)
    image_cords = np.array(image_cords, dtype=np.float32)

    #calculate transform matrix
    if len(real_cords) >= 4 and len(image_cords) >= 4:
        transform_matrix, _ = cv2.findHomography(image_cords, real_cords, cv2.RANSAC, 5)
    else:
        return None

    transformed_image = cv2.warpPerspective(image, transform_matrix, (x_length, y_length))

    return transformed_image

def generate_paths(transformed_image, tag_length=85, tag_x_d=1860, tag_y_d=1030):
    x_length, y_length = 2 * tag_length + tag_x_d, 2 * tag_length + tag_y_d

    #blur image to soften glare
    blurred = cv2.GaussianBlur(transformed_image, (5, 5), 0)

    # cv2.imshow("blurred", blurred)
    # cv2.waitKey(0)

    binary = cv2.adaptiveThreshold(
        blurred,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        21,  # Block size: How large of a local area to look at (must be odd)
        10  # C-value: How much to subtract from the local mean to tune out background noise
    )

    #get the skeleton of the image
    skeleton = cv2.ximgproc.thinning(binary, thinningType=cv2.ximgproc.THINNING_ZHANGSUEN)

    # cut edges
    skeleton[0:20, 0:x_length] = 0
    skeleton[y_length - 20:y_length, 0:x_length] = 0
    skeleton[0:y_length, 0:20] = 0
    skeleton[0:y_length, x_length - 20:x_length] = 0

    # cut corners
    skeleton[0:tag_length + 3, 0:tag_length + 3] = 0
    skeleton[0:tag_length + 3, x_length - 3 - tag_length:x_length] = 0
    skeleton[y_length - 3 - tag_length:y_length, 0:tag_length + 3] = 0
    skeleton[y_length - 3 - tag_length:y_length, x_length - 3 - tag_length:x_length + 3] = 0

    # cv2.imshow("skeleton",skeleton)
    # cv2.waitKey(0)

    #normalize the pixels to be of value 1
    normal = skeleton // 255

    #kernel adds the surrounding pixel values
    kernel = np.array([[1, 1, 1],
                       [1, 10, 1],
                       [1, 1, 1]], dtype=np.uint8)

    #build up a map of the features
    filtered = convolve(normal, kernel, mode='constant', cval=0)

    #10 = isolated dot
    #11 = endpoint
    #12 = line
    #13 >= junction

    endpoints = []

    # visited grid for dfs
    M, N = len(normal), len(normal[0])

    for i in range(len(filtered)):
        for j in range(len(filtered[0])):
            if filtered[i][j] == 11:
                endpoints.append((i,j))

    output_path = []

    #dfs to follow the path from the endpoints
    def dfs(x,y,output):
        stack = [(x,y)]
        prev = (-1,-1)

        while stack:
            xn, yn = stack.pop()

            #ignore if the euclidean distance is more than 5
            if normal[xn][yn] == 255 or normal[xn][yn] == 0 or (prev != (-1,-1) and math.dist(prev,(xn,yn)) > 10):
                # mark visited
                normal[xn][yn] = 255
                continue

            #add to output and mark visited
            normal[xn][yn] = 255
            output.append((yn, xn))
            prev = (xn,yn)

            for xd, yd in [(xn - 1, yn), (xn - 1, yn + 1), (xn, yn + 1), (xn + 1, yn + 1),
                           (xn + 1, yn), (xn + 1, yn - 1), (xn, yn - 1), (xn - 1, yn - 1)]:
                if xd < 0 or xd >= M or yd < 0 or yd >= N:
                    continue
                else:
                    stack.append((xd, yd))

    #loop through all the endpoints and gather the paths
    while endpoints:
        start = endpoints.pop()
        endpoint_output = []
        dfs(start[0], start[1], endpoint_output)

        if endpoint_output:
            endpoint_output.reverse()
            output_path.append(endpoint_output)

    return output_path

def visualize_paths(paths, height, width):
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
            cv2.circle(canvas, path[0], radius=3, color=(0, 0, 255), thickness=-1)

    # Display the result
    cv2.imshow("DFS Paths Visualization", canvas)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def generate_gcode_from_image(file_name: str, feedrate=3000, output_path_name="commands", tag_length=85, tag_x_d=1860, tag_y_d=1030):
    file_path = Path(__file__).parent.parent / "data" / "image_inputs" / file_name

    transformed_image = generate_transformed_image(file_path,tag_length,tag_x_d,tag_y_d)

    # cv2.imshow("transformed_image", transformed_image)
    # cv2.waitKey(0)

    paths = generate_paths(transformed_image)

    h, w = transformed_image.shape[:2]
    visualize_paths(paths, h, w)

    return generate_gcode_from_path(paths, False, feedrate, output_path_name)

generate_gcode_from_image(file_name="test.jpg", output_path_name="test")


