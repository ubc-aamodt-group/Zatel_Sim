import env
import sys
import math

import random
import math
import numpy as np
import colorsys
import itertools

from modules.heatmap_handler import get_simplified_heatmap_pixels, Heatmap
from modules.file_handler import get_file, append_coordinates
from modules.helper_methods import dprint


def g_lin(v):
    return v


def g_exp(v):
    return math.pow(v, 5)


def amplify_temperature(v):
    nv = v
    section_size = env.configs.section_width * env.configs.section_height
    offset = section_size / env.configs.num_representative_pixels

    f = lambda g, x, o: (1-o)*g(x) + o 

    if env.configs.distribution[5:] == 'lin':
        nv = f(g_lin, v, offset)
    elif env.configs.distribution[5:] == 'exp':
        nv = f(g_exp, v, offset)

    return nv


def temperatures_to_percentages(colors):
    to_hues = list(map(lambda c: colorsys.rgb_to_hsv(c[0], c[1], c[2])[0],
                       colors))
    to_hues = list(map(lambda h: 1 - ((h + 0.14) % 1.0), to_hues))
    amplified = list(map(lambda v: amplify_temperature(v), to_hues))
    s = sum(amplified)
    return list(map(lambda v: v/s, amplified))


def get_distributions(color_maps):
    dp = env.configs.distribution

    if (env.configs.distribution == 'uniform'):
        dp = [np.concatenate(mp).sum() / (env.configs.width * env.configs.height) for _, mp in color_maps]
    elif (env.configs.distribution[0:5] == 'temp-'):
        colors = list(map(lambda cm: cm[0], color_maps))
        dp = temperatures_to_percentages(colors)

    return dp


def select_boxes_for_color_map(color_map, num_boxes, bndrs):
    num_of_pixels = env.configs.width * env.configs.height
    MAX_ITERATIONS = int(3 * num_of_pixels)

    dprint(env.plvl.info, f"Num of boxes = {num_boxes}")

    boxes = []
    _, mp = color_map

    valid_points = [[(j, i) if e else None for j, e in enumerate(v)] for i, v in enumerate(mp)]
    valid_points = [list(filter(lambda k: k is not None, v)) for v in valid_points]
    valid_points = list(itertools.chain(*valid_points))

    valid_points = list(filter(lambda p: (p[0], p[1]) in bndrs, valid_points))

    valid_points = list(filter(lambda p: (p[0]+1) % env.configs.section_width == 0 or p[0] % env.configs.section_width == 0, valid_points))

    if not valid_points:
        dprint(env.plvl.warn, "Wasn't able to select boxes")
        return boxes

    copy_valid_points = valid_points.copy()
    for p in copy_valid_points:
        new_p = (p[0] - env.configs.section_width, p[1])
        if (new_p[0] >= 0 and new_p[1] >= 0
            and new_p not in valid_points):
            valid_points.append(new_p)

    num_added = 0
    num_iterations = 0
    while num_added != num_boxes:
        num_iterations = num_iterations + 1

        # pick a random coord
        # p = random.randint(0, num_of_pixels - 1)
        # y = p // env.configs.width
        # x = p % env.configs.width
        x, y = random.choice(valid_points)

        valid_coord = True

        # check if in bounds
        if (x + env.configs.section_width >= env.configs.width or
            y + env.configs.section_height >= env.configs.height):
            valid_coord = False
            continue

        if not valid_coord:
            continue

        # check if intersects with previous boxes
        if num_iterations < MAX_ITERATIONS:
            for box in boxes:
                bx, by = box
                if (x <= bx + env.configs.section_width and
                    x + env.configs.section_width >= bx and
                    y <= by + env.configs.section_height and
                    y + env.configs.section_height >= by):
                    valid_coord = False
                    continue

        if not valid_coord:
            continue

        # check if fills map
        # if number of max iterations has exceeded,
        # just choose a valid pixel as the top-left border
        if num_iterations < MAX_ITERATIONS and not env.configs.enable_edges:
            for i in range(y, y + env.configs.section_height):
                for j in range(x, x + env.configs.section_width):
                    if not mp[i][j]:
                        valid_coord = False
                        break

        elif env.configs.enable_edges:
            found_coord = False

            for i in range(y, y + env.configs.section_height):
                for j in range(x, x + env.configs.section_width):
                    if mp[i][j]:
                        found_coord = True
                        break

            valid_coord = found_coord

        else:
            dprint(env.plvl.warn, "Exceeded max iterations")
            valid_coord = mp[y][x]

        if not valid_coord:
            continue

        # no intersections, can use this coord
        boxes.append((x, y))
        num_added = num_added + 1
        dprint(env.plvl.info, f"Done boxes {num_added}/{num_boxes}")

    dprint(env.plvl.info, "Selected all boxes\n")

    return boxes


def add_pixels_in_boxes(boxes, out, bndrs):
    for box in boxes:
        x, y = box
        for i in range(0, env.configs.section_height):
            for j in range(0, env.configs.section_width):
                nx, ny = x + j, y + i
                if (nx, ny) in bndrs:
                    append_coordinates(out, nx, ny)


def get_percentage_to_trace(heatmap_labels, bndrs, colors):
    s = 0.0

    for coord in bndrs:
        s += colors[int(heatmap_labels[coord[1], coord[0]])]

    r = s / len(bndrs)
    return r


def select_sections(bndrs, out):

    # get simplified heatmap information
    heatmap_info = get_simplified_heatmap_pixels(env.configs.heatmap)

    # extract color maps from the heatmap (black and white)
    color_maps = []
    for i, color in enumerate(heatmap_info.centers):
        vf = np.vectorize(lambda e: e == i)
        color_map = vf(heatmap_info.labels)
        color_maps.append((color, color_map.reshape(heatmap_info.shape)))

    # sort color maps by temperature from cold to hot
    # rotate the wheel s.t. at 0 hue -> `hot` values
    color_maps.sort(key=lambda color_map:
                    1 -
                    ((colorsys.rgb_to_hsv(*color_map[0].tolist())[0] + 0.14)
                     % 1.0))

    distribution_percentages = get_distributions(color_maps)

    # update num_representative_pixels
    cluster_colors = list(map(lambda color_map:
                         1 - ((colorsys.rgb_to_hsv(*color_map[0].tolist())[0] + 0.14) % 1.0),
                         color_maps))
    heatmap_pixels = heatmap_info.labels.reshape(heatmap_info.shape)
    pr = get_percentage_to_trace(heatmap_pixels, bndrs, cluster_colors)
    pr = max(env.configs.min_trace_perc, pr * env.configs.num_pixels_scale)

    env.configs.num_representative_pixels = len(bndrs) * pr
    if (env.configs.const_percentage >= 0.0):
        env.configs.num_representative_pixels = len(bndrs) * env.configs.const_percentage
    env.change_configs(env.configs)

    # get number of boxes to be selected
    num_sections = int(math.ceil(env.configs.num_representative_pixels /
                       (env.configs.section_width * env.configs.section_height)))

    # test for only red for now
    all_boxes = []
    for color_map, percentage in zip(color_maps, distribution_percentages):
        k = int(math.ceil(percentage * num_sections))
        boxes = select_boxes_for_color_map(color_map, k, bndrs)
        all_boxes.append(boxes)

    all_boxes = list(itertools.chain(*all_boxes))
    add_pixels_in_boxes(all_boxes, out, bndrs)
