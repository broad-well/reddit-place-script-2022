#!/usr/bin/env python3

import os
import os.path
import math
import ssl
from typing import Optional, Tuple
from urllib.request import urlretrieve
import requests
from requests_tor import RequestsTor
import json
import time
import threading
import logging
import colorama
import argparse
import sys
import subprocess
import sched
import auth
from io import BytesIO
import urllib
from websocket import create_connection
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
from PIL import ImageColor
from PIL import Image
import random


from mappings import color_map, name_map

# Option remains for legacy usage
# equal to running
# python main.py --verbose
verbose_mode = False

VERSION = 4


canvas_id = 0

# function to convert rgb tuple to hexadecimal string
def rgb_to_hex(rgb):
    return ("#%02x%02x%02x" % rgb).upper()


# Get a more verbose color indicator from a pixel color ID
def color_id_to_name(color_id):
    if color_id in name_map.keys():
        return "{} ({})".format(name_map[color_id], str(color_id))
    return "Invalid Color ({})".format(str(color_id))


# function to find the closest rgb color from palette to a target rgb color
def closest_color(target_rgb, rgb_colors_array_in):
    r, g, b = target_rgb[:3]  # trim rgba tuple to rgb if png

    color_diffs = []
    for color in rgb_colors_array_in:
        cr, cg, cb = color
        color_diff = math.sqrt((r - cr) ** 2 + (g - cg) ** 2 + (b - cb) ** 2)
        color_diffs.append((color_diff, color))
    return min(color_diffs)[1]


# method to draw a pixel at an x, y coordinate in r/place with a specific color
def set_pixel_and_check_ratelimit(
    access_token_in, x, y, color_index_in=18, canvas_index=1
):
    debug_dry_run = False
    tag = canvas_index
    if tag == 4:
        logging.info(
            f"Attempting to place {color_id_to_name(color_index_in)} pixel at {x-500}, {y} on canvas {canvas_index}"
        )
    elif tag == 2:
        logging.info(
            f"Attempting to place {color_id_to_name(color_index_in)} pixel at {x+500}, {y-1000} on canvas {canvas_index}"
        )
    else:
        logging.info(
            f"Attempting to place {color_id_to_name(color_index_in)} pixel at {x-500}, {y-1000} on canvas {canvas_index}"
        )

    url = "https://gql-realtime-2.reddit.com/query"

    payload = json.dumps(
        {
            "operationName": "setPixel",
            "variables": {
                "input": {
                    "actionName": "r/replace:set_pixel",
                    "PixelMessageData": {
                        "coordinate": {"x": x % 1000, "y": y % 1000},
                        "colorIndex": color_index_in,
                        "canvasIndex": tag,
                    },
                }
            },
            "query": 'mutation setPixel($input: ActInput!) {\n  act(input: $input) {\n    data {\n      ... on BasicMessage {\n        id\n        data {\n          ... on GetUserCooldownResponseMessageData {\n            nextAvailablePixelTimestamp\n            __typename\n          }\n          ... on SetPixelResponseMessageData {\n            timestamp\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n'
        }
    )
    headers = {
        "Accept": "*/*",
        "origin": "https://garlic-bread.reddit.com",
        "Referer": "https://garlic-bread.reddit.com/",
        "apollographql-client-name": "garlic-bread",
        "apollographql-client-version": "0.0.1",
        "Authorization": "Bearer " + access_token_in,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    rt = RequestsTor()

    if not debug_dry_run:
        logging.debug(f'requesting placement {headers} {payload}')
        response = rt.request("POST", url, headers=headers, data=payload)
        logging.debug(f"Received response: {response.text}")
    global directed_to_run
    # There are 2 different JSON keys for responses to get the next timestamp.
    # If we don't get data, it means we've been rate limited.
    # If we do, a pixel has been successfully placed.
    if not debug_dry_run and response.json()["data"] is None:
        waitTime = math.floor(
            response.json()["errors"][0]["extensions"]["nextAvailablePixelTs"]
        )
        logging.info(
            f"{colorama.Fore.RED}Failed placing pixel: rate limited {colorama.Style.RESET_ALL}"
        )
        # report pixel drawing to the director
        if conn is not None and conn.connected:
            conn.send(f'failed-to-place {x} {y} {color_index_in}')
            logging.info('informed director of failure to place')
        else:
            logging.warn('could not report placement to director (disconnected)')
            logging.error('cannot place colors without director connection. stopping.')
            directed_to_run = False
    else:
        waitTime = math.floor(
            response.json()["data"]["act"]["data"][0]["data"][
                "nextAvailablePixelTimestamp"
            ]
        ) if not debug_dry_run else 5
        logging.info(
            f"{colorama.Fore.GREEN}Succeeded placing pixel {colorama.Style.RESET_ALL}"
        )
        # report pixel drawing to the director
        if conn is not None and conn.connected:
            conn.send(f'placed {x} {y} {color_index_in}')
            logging.info('informed director of placement')
        else:
            logging.warn('could not report placement to director (disconnected)')
            logging.error('cannot place colors without director connection. stopping.')
            directed_to_run = False

    # THIS COMMENTED CODE LETS YOU DEBUG THREADS FOR TESTING
    # Works perfect with one thread.
    # With multiple threads, every time you press Enter you move to the next one.
    # Move the code anywhere you want, I put it here to inspect the API responses.

    # import code

    # code.interact(local=locals())

    # Self-check: Is this effective?
    time.sleep(10)
    logging.debug('self-checking if placement went through')
    response = rt.request("POST", url, headers=headers, data=json.dumps(
        {
            "operationName": "pixelHistory", 
            "variables":{
                "input":{
                    "actionName": "r/replace:get_tile_history",
                    "PixelMessageData": {
                        "coordinate":{
                            "x":x,"y":y
                        },
                        "colorIndex":0,
                        "canvasIndex":tag
                    }
                }
            },
            "query": "mutation pixelHistory($input: ActInput!) {\n  act(input: $input) {\n    data {\n      ... on BasicMessage {\n        id\n        data {\n          ... on GetTileHistoryResponseMessageData {\n            lastModifiedTimestamp\n            userInfo {\n              userID\n              username\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n"
        }
    ))
    logging.warn(f"{tag} {x} {y} last placed by {response.json()['data']['act']['data'][0]['data']['userInfo']['username']}")

    # Reddit returns time in ms and we need seconds, so divide by 1000
    return waitTime / 1000


def get_board(access_token_in, tag=None):
    global pixel_x_start, pixel_y_start, canvas_id
    if tag is None:
        tag = canvas_id
    logging.info(f"Getting board {tag}")
    ws = create_connection(
        "wss://gql-realtime-2.reddit.com/query", origin="https://garlic-bread.reddit.com"
    )
    ws.send(
        json.dumps(
            {
                "type": "connection_init",
                "payload": {"Authorization": "Bearer " + access_token_in},
            }
        )
    )
    ws.recv()
    ws.send(
        json.dumps(
            {
                "id": "1",
                "type": "start",
                "payload": {
                    "variables": {
                        "input": {
                            "channel": {
                                "teamOwner": "GARLICBREAD",
                                "category": "CONFIG",
                            }
                        }
                    },
                    "extensions": {},
                    "operationName": "configuration",
                    "query": "subscription configuration($input: SubscribeInput!) {\n  subscribe(input: $input) {\n    id\n    ... on BasicMessage {\n      data {\n        __typename\n        ... on ConfigurationMessageData {\n          colorPalette {\n            colors {\n              hex\n              index\n              __typename\n            }\n            __typename\n          }\n          canvasConfigurations {\n            index\n            dx\n            dy\n            __typename\n          }\n          canvasWidth\n          canvasHeight\n          __typename\n        }\n      }\n      __typename\n    }\n    __typename\n  }\n}\n",
                },
            }
        )
    )
    ws.recv()
    ws.send(
        json.dumps(
            {
                "id": "2",
                "type": "start",
                "payload": {
                    "variables": {
                        "input": {
                            "channel": {
                                "teamOwner": "GARLICBREAD",
                                "category": "CANVAS",
                                "tag": str(tag)
                            }
                        }
                    },
                    "extensions": {},
                    "operationName": "replace",
                    "query": "subscription replace($input: SubscribeInput!) {\n  subscribe(input: $input) {\n    id\n    ... on BasicMessage {\n      data {\n        __typename\n        ... on FullFrameMessageData {\n          __typename\n          name\n          timestamp\n        }\n        ... on DiffFrameMessageData {\n          __typename\n          name\n          currentTimestamp\n          previousTimestamp\n        }\n      }\n      __typename\n    }\n    __typename\n  }\n}\n",
                },
            }
        )
    )

    file = ""
    while True:
        temp = json.loads(ws.recv())
        if temp["type"] == "data":
            msg = temp["payload"]["data"]["subscribe"]
            if msg["data"]["__typename"] == "FullFrameMessageData":
                file = msg["data"]["name"]
                break

    ws.close()

    boardimg = BytesIO(requests.get(file, stream=True).content)
    logging.info(f"Received board image: {file}")

    return boardimg


def get_unset_pixel(boardimg, x, y) -> Optional[Tuple[int, int, Tuple[int, int, int]]]:
    pix2 = Image.open(boardimg).convert("RGBA").load()
    num_loops = 0
    lock.acquire()
    unset_pixels = set()
    while True:
        x += 1

        if x >= image_width:
            y += 1
            x = 0

        if y >= image_height:
            if num_loops >= 1:
                break
            y = 0
            num_loops += 1
        # logging.debug(f"{x+pixel_x_start}, {y+pixel_y_start}")
        # logging.debug(f"{x}, {y}, boardimg, {image_width}, {image_height}")

        target_rgb = pix[x, y]
        if target_rgb[3] > 50:
            target_rgb = target_rgb[:3]
            new_rgb = closest_color(target_rgb, rgb_colors_array)
            if pix2[(x + pixel_x_start)%1000, (y + pixel_y_start)%1000][:3] != new_rgb:
                logging.debug(
                    f"{(x + pixel_x_start, y + pixel_y_start)} incorrect: {pix2[(x + pixel_x_start)%1000, (y + pixel_y_start)%1000][:3]}, {new_rgb}, {new_rgb != (69, 42, 0)}, {pix2[x%1000, y%1000][:3] != new_rgb,}"
                )
                if new_rgb != (69, 42, 0):
                    unset_pixels.add((x, y, new_rgb))
                else:
                    print("TransparentPixel")
    logging.info(f'found {len(unset_pixels)} incorrect pixels in current canvas')
    if len(unset_pixels) == 0:
        lock.release()
        return None
    # Selection logic here
    (x, y, new_rgb) = random.choice(list(unset_pixels))
    logging.debug(
        f"Replacing {pix2[(x+pixel_x_start)%1000, (y+pixel_y_start)%1000]} pixel at: {x+pixel_x_start},{y+pixel_y_start} with {new_rgb} color"
    )
    lock.release()
    return x, y, new_rgb


def make_rgb_colors_array():
    out = []
    for color_hex, color_index in color_map.items():
        rgb_array = ImageColor.getcolor(color_hex, "RGB")
        out.append(rgb_array)
    return out


# method to define the color palette array
def init_rgb_colors_array():
    global rgb_colors_array
    rgb_colors_array = make_rgb_colors_array()
    logging.debug(f"Available colors for rgb palette: {rgb_colors_array}")


# method to read the input image.jpg file
def load_image():
    global pix
    global image_width
    global image_height
    global image_extension

    # read and load the image to draw and get its dimensions
    valid_image_extensions = [
        ".png",
        ".jpg",
        ".jpeg",
    ]  # List your valid image extensions here

    image_path = None
    for extension in valid_image_extensions:
        path = os.path.join(os.path.abspath(os.getcwd()), "image" + extension)
        if os.path.exists(path):
            image_path = path
            image_extension = extension
            break

    if image_path is None:
        sys.exit("No valid image path found!")

    print("Loading image from " + image_path)
    im = Image.open(image_path)
    lock.acquire()
    pix = im.load()
    lock.release()
    logging.info(f"Loaded image size: {im.size}")
    image_width, image_height = im.size


# task to draw one important incorrect pixel selected from the input image
def task(credentials_index):
    # whether image should keep drawing itself
    repeat_forever = True

    while True:
        if os.getenv("ENV_UNVERIFIED_PLACE_FREQUENCY") is not None:
            if bool(os.getenv("ENV_UNVERIFIED_PLACE_FREQUENCY")):
                pixel_place_frequency = 1230
            else:
                pixel_place_frequency = 330
        else:
            pixel_place_frequency = 330

        next_pixel_placement_time = math.floor(time.time()) + pixel_place_frequency

        # pixel drawing preferences
        global pixel_x_start, pixel_y_start


        # string for time until next pixel is drawn
        update_str = ""

        # reference to globally shared variables such as auth token and image
        global access_tokens
        global access_token_expires_at_timestamp

        # boolean to place a pixel the moment the script is first run
        # global first_run
        global first_run_counter
        global directed_to_run

        # refresh auth tokens and / or draw a pixel
        while True:
            # reduce CPU usage
            time.sleep(2)

            if not directed_to_run:
                logging.debug('skipping iteration because not directed to run')
                continue

            # get the current time
            current_timestamp = math.floor(time.time())

            # log next time until drawing
            time_until_next_draw = next_pixel_placement_time - current_timestamp
            new_update_str = (
                str(time_until_next_draw) + " seconds until next pixel is drawn"
            )
            if update_str != new_update_str and time_until_next_draw % 10 == 0:
                update_str = new_update_str
                logging.info(f"Thread #{credentials_index} :: {update_str}")

            # refresh access token if necessary
            if (
                access_tokens[credentials_index] is None
            ):
                logging.info(f"Thread #{credentials_index} :: Refreshing access token")

                # developer's reddit username and password
                try:
                    username = json.loads(os.getenv("ENV_PLACE_USERNAME"))[
                        credentials_index
                    ]
                    password = json.loads(os.getenv("ENV_PLACE_PASSWORD"))[
                        credentials_index
                    ]
                except IndexError:
                    print(
                        "Array length error: are you sure your credentials have an equal amount of items?\n",
                        "Example for 2 accounts:\n",
                        'ENV_PLACE_USERNAME=\'["Username1", "Username2]\'\n',
                        'ENV_PLACE_PASSWORD=\'["Password", "Password"]\'\n',
                        "Note: There can be duplicate entries, but every array must have the same amount of items.",
                    )
                    exit(1)

                try:
                    access_tokens[credentials_index] = auth.get_access_token(username, password, logging)
                except:
                    repeat_forever = False
                    logging.fatal(f"Bad account {username}")
                    break
                # access_token_type = response_data["token_type"]  # this is just "bearer"

            # draw pixel onto screen
            if access_tokens[credentials_index] is not None and (
                current_timestamp >= next_pixel_placement_time
                or first_run_counter <= credentials_index
            ):

                # place pixel immediately
                # first_run = False
                first_run_counter += 1

                # get target color
                # target_rgb = pix[current_r, current_c]

                # get current pixel position from input image and replacement color
                optional_pixel = get_unset_pixel(
                    get_board(access_tokens[credentials_index]),
                    0,
                    0,
                )

                logging.debug(f"Thread #{credentials_index} :: optional_pixel={optional_pixel}")
                if optional_pixel is not None:
                    current_r, current_c, new_rgb = optional_pixel

                    # get converted color
                    new_rgb_hex = rgb_to_hex(new_rgb)
                    pixel_color_index = color_map[new_rgb_hex]

                    # draw the pixel onto r/place
                    logging.debug(f"PLACEMENT {pixel_x_start} {pixel_y_start} {current_c} {current_r}")
                    next_pixel_placement_time = set_pixel_and_check_ratelimit(
                        access_tokens[credentials_index],
                        pixel_x_start + current_r,
                        pixel_y_start + current_c,
                        pixel_color_index,
                        canvas_id
                    ) + random.randint(60, 120)
                else:
                    logging.info(f"Thread {credentials_index} :: No pixels are wrong! Taking a 5 second break")
                    time.sleep(3) # the last second is slept at the beginning of the next loop iteration



        # except:
        #     print("__________________")
        #     print("Thread #" + str(credentials_index))
        #     print("Error refreshing tokens or drawing pixel")
        #     print("Trying again in 5 minutes...")
        #     print("__________________")
        #     time.sleep(5 * 60)

        if not repeat_forever:
            break


def get_last_modified_commit() -> str:
    return subprocess.run(["git", "log", "-1", "--format=%H", "image.png"], capture_output=True, text=True).stdout

def pull_image(scheduler: sched.scheduler):
    print("Attempting to pull image...")
    global last_modified_commit

    if (last_modified_commit is None):
        last_modified_commit = get_last_modified_commit()

    subprocess.run(["git", "pull"], capture_output=True, text=True)

    commit_after_pull = get_last_modified_commit()
    if commit_after_pull != last_modified_commit:
        load_image()
        print("Load image called!")
        last_modified_commit = commit_after_pull
    else:
        print("Not modified!")
    scheduler.enter(scheduler_delay, 1, pull_image, (scheduler,))
    

def director_comms():
    url = os.getenv("ENV_DIRECTOR_URL")
    if url is None:
        logging.fatal('This bot is managed by a director. Please ask for the Director URL and set it to ENV_DIRECTOR_URL in .env.')
        exit()

    def read_target(conn, recvd):
        (targ, targ_canvas, targ_xs, targ_ys, img_url) = recvd.split(' ')
        assert targ == 'target'
        global canvas_id
        canvas_id = int(targ_canvas)
        os.environ['ENV_DRAW_X_START'] = str(int(targ_xs))
        os.environ['ENV_DRAW_Y_START'] = str(int(targ_ys))
        global pixel_x_start, pixel_y_start
        logging.debug(f"TARGET {targ} {targ_canvas} {targ_xs} {targ_ys}")
        pixel_x_start = int(targ_xs)
        pixel_y_start = int(targ_ys)
        logging.info('Got target info from director, downloading image')
        target_img = 'image.png' if '.png' in img_url else 'image.jpg'
        logging.info('getting new target image from ' + img_url)
        req = requests.get(img_url, headers={'User-Agent':'Mozilla/5.0'})
        with open(target_img, 'wb') as _file:
            _file.write(req.content)
        logging.info('Downloaded target image')
        load_image()
        conn.send('ok')

    #ctx = ssl.create_default_context()
    #ctx.load_verify_locations('mcert.cer')

    run = True
    global directed_to_run, conn
    while run:
        try:
            logging.info('contacting director at ' + url)
            conn = create_connection(url)# sslopt={'context': ctx})
            conn.send(f'hello {VERSION}')
            read_target(conn, conn.recv())
            while True:
                msg = conn.recv()
                if msg == 'stop':
                    directed_to_run = False
                    logging.info('Directed to stop running')
                    conn.send('ok')
                elif msg == 'start':
                    directed_to_run = True
                    logging.info('Directed to start running')
                    conn.send('ok')
                elif msg == 'ping':
                    conn.send('pong')
                elif msg == 'stats':
                    conn.send('[]')
                elif msg.startswith('target'):
                    read_target(conn, msg)
                elif msg == 'out-of-date':
                    logging.warning('Director says this client is out-of-date! Check https://github.com/broad-well/reddit-place-umich-botnet for updates.')
        except Exception as e:
            logging.error('director connection lost %s, retrying in 5 seconds' % e)
            time.sleep(5)


# # # # #  MAIN # # # # # #


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    colorama.init()
    parser.add_argument(
        "-v",
        "--verbose",
        help="Be verbose",
        action="store_const",
        dest="loglevel",
        const=logging.DEBUG,
        default=logging.INFO,
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=(logging.DEBUG if verbose_mode else args.loglevel),
        format="[%(asctime)s] :: [%(levelname)s] - %(message)s",
        datefmt="%d-%b-%y %H:%M:%S",
    )
    logging.info("place-script started")
    if os.path.exists("./.env"):
        # load env variables
        load_dotenv()
    else:
        envfile = open(".env", "w")
        envfile.write(
            """ENV_PLACE_USERNAME='["username"]'
ENV_PLACE_PASSWORD='["password"]'
ENV_DIRECTOR_URL='ws://botnet.umich.place:4523'"""
        )
        print(
            "No .env file found. A template has been created for you.",
            "Read the README and configure it properly.",
            "Right now, it's full of example data, so you ABSOLUTELY MUST edit it.",
        )
        logging.fatal("No .env file found")
        exit()

    # color palette
    rgb_colors_array = []

    # auth variables
    access_tokens = []
    access_token_expires_at_timestamp = []

    # image.jpg information
    pix = None
    image_width = None
    image_height = None

    lock = threading.Lock()

    # Last commit hash in which image.png was modified
    last_modified_commit = None

    # place a pixel immediately
    # first_run = True
    first_run_counter = 0

    # director control
    directed_to_run = False
    pixel_x_start = None
    pixel_y_start = None
    conn = None # connection to director, needed to report color updates

    # get color palette
    init_rgb_colors_array()

    # load the pixels for the input image
    load_image()

    # get number of concurrent threads to start
    num_credentials = len(json.loads(os.getenv("ENV_PLACE_USERNAME")))

    # define delay between starting new threads
    if os.getenv("ENV_THREAD_DELAY") is not None:
        delay_between_launches_seconds = int(os.getenv("ENV_THREAD_DELAY"))
    else:
        delay_between_launches_seconds = 3

    scheduler = sched.scheduler(time.time, time.sleep)
    scheduler_delay = 1800
    #scheduler.enter(scheduler_delay, 1, pull_image, (scheduler,))
    thread0 = threading.Thread(target=scheduler.run)
    thread0.start()

    thread2 = threading.Thread(target=director_comms)
    thread2.start()

    # launch a thread for each account specified in .env
    for i in range(num_credentials):
        # run the image drawing task
        access_tokens.append(None)
        access_token_expires_at_timestamp.append(math.floor(time.time()))
        thread1 = threading.Thread(target=task, args=[i])
        thread1.start()
        time.sleep(delay_between_launches_seconds)
