import cv2
import numpy as np

from path_functions import greedy

def generate_gcode_from_image(file_path: str, tag_length=85, tag_x_d=1860, tag_y_d=1030):
    #for april tags, the coordinates within the april tags are in the following order: top left, top right, bottom right, bottom left

    x_length, y_length = 2*tag_length + tag_x_d, 2*tag_length + tag_y_d

    #determine real-world positions of the whiteboard april tags
    real_corners = {}

    for i, top_left in enumerate([(0, 0), (tag_length+tag_x_d, 0), (0, tag_length+tag_y_d), (tag_length+tag_x_d, tag_length+tag_y_d)]):
        for x, y in top_left:
            real_corners[i+1] = [(x,y), (x+tag_length,y), (x+tag_length,y+tag_length), (x,y+tag_length)]

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

    for id, corner in zip(ids, corners):
        real_cords.extend(real_corners[id])
        image_cords.extend(corner)

    real_cords = np.array(real_cords,dtype=np.float32)
    image_cords = np.array(image_cords, dtype=np.float32)

    #calculate transform matrix
    if len(real_cords) >= 4 and len(image_cords) >= 4:
        transform_matrix, _ = cv2.findHomography(image_cords, real_cords, cv2.RANSAC, 5)
    else:
        return None

    transformed_image = cv2.warpPerspective(image, transform_matrix, (x_length, y_length))

    # cut edges
    transformed_image[0:5, 0:x_length] = 255
    transformed_image[y_length-5:y_length, 0:x_length] = 255
    transformed_image[0:y_length, 0:5] = 255
    transformed_image[0:y_length, x_length-5:x_length] = 255

    # cut corners
    transformed_image[0:tag_length, 0:tag_length] = 255
    transformed_image[0:tag_length, x_length-tag_length:x_length] = 255
    transformed_image[y_length-tag_length:y_length, 0:tag_length] = 255
    transformed_image[y_length-tag_length:y_length, x_length-tag_length:x_length] = 255

    return transformed_image

def generate_gcode(transformed_image, feedrate: int, output_path_name="commands"):

    pass