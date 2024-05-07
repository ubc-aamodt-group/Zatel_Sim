import cv2
import numpy as np

import env


def get_collection_coords(collection: str):
    """
    Return coordinates to trace from a coordinates file
    """
    collection_file = None
    try:
        collection_file = open(collection, "r")
    except:
        print("GET COLLECTION COORDS")

    pixel_coords = []

    while True:
        line = collection_file.readline()
        if not line:
            break

        x, y = line.split(' ')
        x = int(x)
        y = int(y)

        index = env.configs.width * y + x

        pixel_coords.append(index)

    collection_file.close()

    return np.array(pixel_coords)


def visualize_selected_pixels(collection: str, out: str):
    """
    output the scene screenshot with the non-traced pixels dimmed
    """
    DIM_SCALE = 5

    img = cv2.imread(env.configs.heatmap)
    img = img // DIM_SCALE
    pixels_as_row = img.reshape((-1, 3))
    
    selected_pixels = get_collection_coords(collection)

    dprint(env.plvl.info, f"Selected Pixels: {selected_pixels}")
    pixels_as_row[selected_pixels] *= DIM_SCALE

    p_img = pixels_as_row.reshape((img.shape))

    p = len(selected_pixels) / (env.configs.width * env.configs.height / env.configs.num_chunks)
    dprint(env.plvl.info, f"Percentage of pixels selected: {p}")

    # cv2.imshow('p_img', p_img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    cv2.imwrite(out, p_img)


def get_closest_product_pair(k):
    """
    Get the closest pair of numbers s.t. n1 x n2 = k, n1 >= n2
    Ex: for 8, closest pair is (4, 2)
    """
    visited = set([])
    c = 1

    while c <= k:
        n = k / c
        if k % c == 0:
            if c in visited or n == c:
                return (c, int(n))
            else:
                visited.add(n)

        c = c + 1

    return (k, 1)


def shader_type_to_code():
    shader_type = 0
    if env.configs.shader_type == "path-tracer":
        shader_type = 0
    elif env.configs.shader_type == "shadow":
        shader_type = 1
    elif env.configs.shader_type == "ambient-occlusion":
        shader_type = 2
    else:
        dprint(env.plvl.warn,
               "Chose shader type 'path tracer' since no correct option chosen")

    return shader_type


def dprint(level, s):
    if env.configs.debug:
        print(f"[{level}] " + str(s))
