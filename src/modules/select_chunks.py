import math

import env
from modules.helper_methods import dprint
from modules.helper_methods import get_closest_product_pair


def select_chunks_coarse_grained(i):
    """
    Splitting the scene into quadrants, picking i-th
    """
    dprint(env.plvl.info, f"Getting {i}-th chunk's coordinates (coarse-grained)...")

    available_coordinates = set()

    w, h = env.configs.width, env.configs.height

    r, c = get_closest_product_pair(env.configs.num_chunks)

    if h >= w:
        r, c = c, r

    sw, sh = math.ceil(w / r), math.ceil(h / c)

    y0 = (i // r) * sh
    x0 = (i % r) * sw

    for yy in range(sh):
        for xx in range(sw):
            x = x0 + xx
            y = y0 + yy
            available_coordinates.add((x, y))

    dprint(env.plvl.info, f"Got the coordinates for {i}-th chunk (coarse-grained)")
    return available_coordinates


def select_chunks_fine_grained(i):
    """
    Splitting the scene into small chunks, picking every i-th
    """
    dprint(plvl.info, f"Getting {i}-th chunk's coordinates (fine-grained)...")

    available_coordinates = set()

    sw, sh = 32, 2

    w, h = env.configs.width, env.configs.height
    n = env.configs.num_chunks

    c, r = math.ceil(w / sw), math.ceil(h / sh)

    for y in range(r):
        for x in range(c):
            k = (i + y + x) % n
            if k == 0:
                for yy in range(sh):
                    for xx in range(sw):
                        x0 = x * sw
                        y0 = y * sh
                        _x = x0 + xx
                        _y = y0 + yy

                        if _x < w and _y < h:
                            available_coordinates.add((_x, _y))

    dprint(env.plvl.info, f"Got the coordinates for {i}-th chunk (fine-grained)")
    return available_coordinates


def select_chunks(i):
    if env.configs.chunks_type == "coarse-grained":
        return select_chunks_coarse_grained(i)
    elif env.configs.chunks_type == "fine-grained":
        return select_chunks_fine_grained(i)
