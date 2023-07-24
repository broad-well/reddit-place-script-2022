import auth
import logging
import canvas_diff
from main import get_board, make_rgb_colors_array
from PIL import Image
from datetime import datetime
import time
import os
import json

colors = make_rgb_colors_array()

token = auth.get_access_token(input('reddit account username:'), input('reddit account password:'), logging)


history = []
for i in range(100000):
    board_img = Image.open(get_board(token, tag=2))
    unset = canvas_diff.unset_pixels(Image.open('watch.png'), board_img, colors, 157, 632)
    # unset = canvas_diff.unset_pixels(Image.open('/Users/michael/Downloads/pixil-frame-0-35.png'), Image.open(get_board(token, tag=0)), colors, 579, 246)
    print(datetime.now(), len(unset))
    if len(unset) >= 20:
        os.system(f'say "M {len(unset)}"')

    # board_img = Image.open(get_board(token, tag=3))
    # unset = canvas_diff.unset_pixels(Image.open('wolverine_inside.png'), board_img, colors, 982, 696)
    # # unset = canvas_diff.unset_pixels(Image.open('/Users/michael/Downloads/pixil-frame-0-35.png'), Image.open(get_board(token, tag=0)), colors, 579, 246)
    # print(datetime.now(), len(unset))
    # if len(unset) >= 20:
    #     os.system(f'say "wolverine {len(unset)}"')
    # history.append([datetime.now().isoformat(), list(unset)])
    time.sleep(5)

with open('diffstats.json', 'w+') as ds:
    json.dump(history, ds)