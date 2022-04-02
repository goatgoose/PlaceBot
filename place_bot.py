import sys

import requests
from bs4 import BeautifulSoup


class Placer:
    LOGIN_URL = "https://www.reddit.com/login"

    def __init__(self):
        self.client = requests.session()
        self.client.headers.update({
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br",
            "accept-languages": "en-US,en;q=0.9",
            "content-type": "application/x-www-form-urlencoded",
            "origin": "https://www.reddit.com",
            "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36"
        })

    def login(self, username, password):
        # get the csrf token
        r = self.client.get(self.LOGIN_URL)

        login_get_soup = BeautifulSoup(r.content, "html.parser")
        csrf_token = login_get_soup.find("input", {"name": "csrf_token"})["value"]

        # authenticate
        r = self.client.post(
            self.LOGIN_URL,
            data={
                "username": username,
                "password": password,
                "dest": "https://www.reddit.com",
                "csrf_token": csrf_token
            }
        )

        assert r.status_code == 200


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("usage: python3 place_bot.py [reddit username] [reddit password]")

    username = sys.argv[1]
    password = sys.argv[2]

    placer = Placer()
    placer.login(username, password)
