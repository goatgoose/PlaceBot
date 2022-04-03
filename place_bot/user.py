import time


class Token:
    EXPIRATION_TIME = 60 * 60 - 10

    def __init__(self, value: str):
        self.value = value

        self.registered = time.time()

    @property
    def expired(self):
        now = time.time()
        return now > self.registered + Token.EXPIRATION_TIME


class User:
    PLACE_TIMEOUT = 60 * 5 + 5

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

        self.client = None
        self.token = None

        self.placed_timestamp = 0

    @property
    def auth_valid(self):
        if not self.token:
            return False
        if self.token.expired:
            return False
        return True

    @property
    def placeable(self):
        now = time.time()
        return now > self.placed_timestamp + User.PLACE_TIMEOUT

    def set_placed(self):
        now = time.time()
        self.placed_timestamp = now
