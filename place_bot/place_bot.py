from enum import Enum
import time
import json
from io import BytesIO

import requests
from bs4 import BeautifulSoup
import websocket
from PIL import Image
import numpy as np
from typing import Tuple

from . import queries

from dataclasses import dataclass


def rgb2hex(r, g, b):
    return f"#{r:02x}{g:02x}{b:02x}"


@dataclass
class Color:
    name: str
    value: int
    hex: str


# fmt: off
colors_by_id = {
    1: Color("DARK_RED",     1,  "BE0039"),
    2: Color("RED",          2,  "FF4500"),
    3: Color("ORANGE",       3,  "FFA800"),
    4: Color("YELLOW",       4,  "FFD635"),
    6: Color("DARK_GREEN",   6,  "00A368"),
    7: Color("GREEN",        7,  "00CC78"),
    8: Color("LIGHT_GREEN",  8,  "7EED56"),
    9: Color("DARK_TEAL",    9,  "00756F"),
    10: Color("TEAL",        10, "009EAA"),
    12: Color("DARK_BLUE",   12, "2450A4"),
    13: Color("BLUE",        13, "3690EA"),
    14: Color("LIGHT_BLUE",  14, "51E9F4"),
    15: Color("INDIGO",      15, "493AC1"),
    16: Color("PERIWINKLE",  16, "6A5CFF"),
    18: Color("DARK_PURPLE", 18, "811E9F"),
    19: Color("PURPLE",      19, "B44AC0"),
    20: Color("PINK",        20, "FF3881"),
    23: Color("LIGHT_PINK",  23, "FF99AA"),
    25: Color("BROWN",       25, "6D482F"),
    26: Color("DARK_BROWN",  26, "9C6926"),
    27: Color("BLACK",       27, "000000"),
    29: Color("GRAY",        29, "898D90"),
    30: Color("LIGHT_GRAY",  30, "D4D7D9"),
    31: Color("WHITE",       31, "FFFFFF"),
}
# fmt: on

colors_by_name = {c.name: c for c in colors_by_id.values()}
colors_by_hex = {c.hex: c for c in colors_by_id.values()}


def color_from_pixel(rgb_im_px) -> Color:
    r, g, b = rgb_im_px
    hex_ = rgb2hex(r, g, b)
    return colors_by_hex[hex_.upper().strip("#")]


class Placer:
    REDDIT_URL = "https://www.reddit.com"
    LOGIN_URL = REDDIT_URL + "/login"
    INITIAL_HEADERS = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/x-www-form-urlencoded",
        "origin": REDDIT_URL,
        "sec-ch-ua": (
            '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"'
        ),
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like"
            " Gecko) Chrome/100.0.4896.60 Safari/537.36"
        ),
    }

    def __init__(self):
        self.client = requests.session()
        self.client.headers.update(self.INITIAL_HEADERS)

        self.token = None
        self.username = ""

    def login(self, username: str, password: str):
        self.username = username
        # get the csrf token
        r = self.client.get(self.LOGIN_URL)
        login_get_soup = BeautifulSoup(r.content, "html.parser")
        csrf_token = login_get_soup.find("input", {"name": "csrf_token"})["value"]
        time.sleep(1)

        # authenticate
        r = self.client.post(
            self.LOGIN_URL,
            data={
                "username": username,
                "password": password,
                "dest": self.REDDIT_URL,
                "csrf_token": csrf_token,
            },
        )
        time.sleep(1)

        assert r.status_code == 200

        # get the new access token
        r = self.client.get(self.REDDIT_URL)
        data_str = (
            BeautifulSoup(r.content, "html.parser")
            .find("script", {"id": "data"})
            .contents[0][len("window.__r = ") : -1]
        )
        data = json.loads(data_str)
        self.token = data["user"]["session"]["accessToken"]

    def place_tile(self, x: int, y: int, color: Color):
        # handle 2nd canvas
        canvas_index = x // 1000
        x -= canvas_index * 1000

        headers = self.INITIAL_HEADERS.copy()
        headers.update(
            {
                "apollographql-client-name": "mona-lisa",
                "apollographql-client-version": "0.0.1",
                "content-type": "application/json",
                "origin": "https://hot-potato.reddit.com",
                "referer": "https://hot-potato.reddit.com/",
                "sec-fetch-site": "same-site",
                "authorization": "Bearer " + self.token,
            }
        )

        r = requests.post(
            "https://gql-realtime-2.reddit.com/query",
            json={
                "operationName": "setPixel",
                "query": queries.SET_PIXEL_QUERY,
                "variables": {
                    "input": {
                        "PixelMessageData": {
                            "canvasIndex": canvas_index,
                            "colorIndex": color.value,
                            "coordinate": {"x": x, "y": y},
                        },
                        "actionName": "r/replace:set_pixel",
                    }
                },
            },
            headers=headers,
        )

        assert r.status_code == 200

        print(f"{self.username} placed {color.name} tile at {x}, {y}")

    def get_map_data(self):
        r = requests.get(self._get_map_url())
        assert r.status_code == 200

        im = Image.open(BytesIO(r.content))
        map_data = self.image_to_data(im, (1000, 1000))

        return map_data

    def maintain_image(self, x: int, y: int, image_path: str):
        """
        :param x: left most x coord
        :param y: top most y coord
        :param image_path: path of the image to maintain
        :param image_shape shape of the image
        """
        im = Image.open(image_path)
        image_shape = (im.size[1], im.size[0])
        im_data = self.image_to_data(im, image_shape)

        while True:
            map_data = self.get_map_data()
            map_slice = map_data[y : y + image_shape[0], x : x + image_shape[1]]

            differing_pixels = self._find_differing_pixels(
                map_slice, im_data, image_shape
            )
            if len(differing_pixels) > 0:
                differing_pixel = differing_pixels[0]
                x_ = differing_pixel[0]
                y_ = differing_pixel[1]
                self.place_tile(x + x_, y + y_, colors_by_id[im_data[y_, x_]])
                time.sleep(60 * 5 + 10)
            else:
                time.sleep(30)

    @staticmethod
    def _find_differing_pixels(map_data, im_data, shape):
        differing_pixels = []
        for y_ in range(shape[0]):
            for x_ in range(shape[1]):
                map_value = map_data[y_, x_]
                im_value = im_data[y_, x_]
                if map_value != im_value:
                    differing_pixels.append((x_, y_))
        return differing_pixels

    @staticmethod
    def image_to_data(image: Image, shape: Tuple[int, int]):
        rgb_im = image.convert("RGB")

        data = np.array([color_from_pixel(px).value for px in rgb_im.getdata()])
        data = np.reshape(data, shape)

        return data

    def _get_map_url(self):
        ws = websocket.create_connection("wss://gql-realtime-2.reddit.com/query")
        ws.send(
            json.dumps(
                {
                    "type": "connection_init",
                    "payload": {"Authorization": "Bearer " + self.token},
                }
            )
        )
        ws.send(
            json.dumps(
                {
                    "type": "start",
                    "id": "1",
                    "payload": {
                        "extensions": {},
                        "operationName": "replace",
                        "query": queries.FULL_FRAME_MESSAGE_SUBSCRIBE_QUERY,
                        "variables": {
                            "input": {
                                "channel": {
                                    "category": "CANVAS",
                                    "tag": "0",
                                    "teamOwner": "AFD2022",
                                }
                            }
                        },
                    },
                }
            )
        )

        while True:
            result = json.loads(ws.recv())
            if "id" not in result:
                continue
            if result["id"] != "1":
                continue
            assert (
                result["payload"]["data"]["subscribe"]["data"]["__typename"]
                == "FullFrameMessageData"
            )
            ws.close()
            return result["payload"]["data"]["subscribe"]["data"]["name"]
