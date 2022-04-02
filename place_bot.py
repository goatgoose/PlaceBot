from enum import Enum
import time
import json

import requests
from bs4 import BeautifulSoup
import websocket

import queries


class Color(Enum):
    RED = 2
    ORANGE = 3
    YELLOW = 4
    DARK_GREEN = 6
    LIGHT_GREEN = 8
    DARK_BLUE = 12
    BLUE = 13
    LIGHT_BLUE = 14
    DARK_PURPLE = 18
    PURPLE = 19
    LIGHT_PINK = 23
    BROWN = 25
    BLACK = 27
    GRAY = 29
    LIGHT_GRAY = 30
    WHITE = 31


class Placer:
    REDDIT_URL = "https://www.reddit.com"
    LOGIN_URL = REDDIT_URL + "/login"
    INITIAL_HEADERS = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/x-www-form-urlencoded",
        "origin": REDDIT_URL,
        "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36"
    }

    def __init__(self):
        self.client = requests.session()
        self.client.headers.update(self.INITIAL_HEADERS)

        self.token = None

    def login(self, username: str, password: str):
        # get the csrf token
        r = self.client.get(self.LOGIN_URL)
        time.sleep(1)

        login_get_soup = BeautifulSoup(r.content, "html.parser")
        csrf_token = login_get_soup.find("input", {"name": "csrf_token"})["value"]

        # authenticate
        r = self.client.post(
            self.LOGIN_URL,
            data={
                "username": username,
                "password": password,
                "dest": self.REDDIT_URL,
                "csrf_token": csrf_token
            }
        )
        time.sleep(1)

        assert r.status_code == 200

        # get the new access token
        r = self.client.get(self.REDDIT_URL)
        data_str = BeautifulSoup(r.content, "html.parser").find("script", {"id": "data"}).contents[0][len("window.__r = "):-1]
        data = json.loads(data_str)
        self.token = data["user"]["session"]["accessToken"]

    def get_map_url(self):
        ws = websocket.create_connection("wss://gql-realtime-2.reddit.com/query")
        ws.send(json.dumps({
            "type": "connection_init",
            "payload": {
                "Authorization": "Bearer " + self.token
            }
        }))
        ws.send(json.dumps({
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
                            "teamOwner": "AFD2022"
                        }
                    }
                }
            }
        }))

        while True:
            result = json.loads(ws.recv())
            if "id" not in result:
                continue
            if result["id"] != "1":
                continue
            assert result["payload"]["data"]["subscribe"]["data"]["__typename"] == "FullFrameMessageData"
            return result["payload"]["data"]["subscribe"]["data"]["name"]

    def place_tile(self, x: int, y: int, color: Color):
        headers = self.INITIAL_HEADERS.copy()
        headers.update({
            "apollographql-client-name": "mona-lisa",
            "apollographql-client-version": "0.0.1",
            "content-type": "application/json",
            "origin": "https://hot-potato.reddit.com",
            "referer": "https://hot-potato.reddit.com/",
            "sec-fetch-site": "same-site",
            "authorization": "Bearer " + self.token
        })

        r = requests.post(
            "https://gql-realtime-2.reddit.com/query",
            json={
                "operationName": "setPixel",
                "query": queries.SET_PIXEL_QUERY,
                "variables": {
                    "input": {
                        "PixelMessageData": {
                            "canvasIndex": 0,
                            "colorIndex": color.value,
                            "coordinate": {
                                "x": x,
                                "y": y
                            }
                        },
                        "actionName": "r/replace:set_pixel"
                    }
                }
            },
            headers=headers
        )

        assert r.status_code == 200
