import logging
import math
from threading import Lock
from typing import Set, Tuple
from PIL import Image

# function to find the closest rgb color from palette to a target rgb color
def closest_color(target_rgb, rgb_colors_array_in):
    r, g, b = target_rgb[:3]  # trim rgba tuple to rgb if png

    color_diffs = []
    for color in rgb_colors_array_in:
        cr, cg, cb = color
        color_diff = math.sqrt((r - cr) ** 2 + (g - cg) ** 2 + (b - cb) ** 2)
        color_diffs.append((color_diff, color))
    return min(color_diffs)[1]


# remember to lock target
def unset_pixels(target: Image, board: Image, rgb_colors_array_in, board_left_x: int, board_top_y: int) -> Set[Tuple[int, int, Tuple[int, int, int]]]:
    pix2 = board.convert('RGBA').load()
    pix_target = target.convert('RGBA').load()
    image_width, image_height = target.size
    num_loops = 0
    x, y = 0, 0
    unset_pixels = set()
    while True:
        x += 1

        if x >= image_width:
            y += 1
            x = 0

        if y >= image_height:
            if num_loops > 1:
                break
            y = 0
            num_loops += 1
        # logging.debug(f"{x+pixel_x_start}, {y+pixel_y_start}")
        # logging.debug(f"{x}, {y}, boardimg, {image_width}, {image_height}")

        target_rgb = pix_target[x, y]
        logging.debug(f'target_rgb at {(x,y)} is {target_rgb}')
        if target_rgb[3] > 50:
            target_rgb = target_rgb[:3]
            new_rgb = closest_color(target_rgb, rgb_colors_array_in)
            if pix2[(x + board_left_x)%1000, (y + board_top_y)%1000][:3] != new_rgb:
                unset_pixels.add((x, y, new_rgb))
    return unset_pixels