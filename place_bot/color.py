from enum import Enum
from collections import namedtuple

color = namedtuple("color", ["id", "hex"])


class Color(Enum):
    DARK_RED = color(1, "BE0039")
    RED = color(2, "FF4500")
    ORANGE = color(3, "FFA800")
    YELLOW = color(4, "FFD635")
    DARK_GREEN = color(6, "00CC78")
    GREEN = color(7, "00CC78")
    LIGHT_GREEN = color(8, "7EED56")
    DARK_TEAL = color(9, "00756F")
    TEAL = color(10, "009EAA")
    DARK_BLUE = color(12, "2450A4")
    BLUE = color(13, "3690EA")
    LIGHT_BLUE = color(14, "51E9F4")
    INDIGO = color(15, "493AC1")
    PERIWINKLE = color(16, "6A5CFF")
    DARK_PURPLE = color(18, "811E9F")
    PURPLE = color(19, "B44AC0")
    PINK = color(20, "FF3881")
    LIGHT_PINK = color(23, "FF99AA")
    BROWN = color(25, "6D482F")
    DARK_BROWN = color(26, "9C6926")
    BLACK = color(27, "000000")
    GRAY = color(29, "898D90")
    LIGHT_GRAY = color(30, "D4D7D9")
    WHITE = color(31, "FFFFFF")

    @staticmethod
    def all():
        # https://stackoverflow.com/a/13286863
        return [
            getattr(Color, attr) for attr in dir(Color)
            if not callable(getattr(Color, attr))
            and not attr.startswith("__")
        ]

    @staticmethod
    def rgb2hex(r, g, b):
        return f"#{r:02x}{g:02x}{b:02x}"

    @staticmethod
    def from_pixel(rgb_im_px) -> 'Color':
        r, g, b = rgb_im_px
        hex_ = Color.rgb2hex(r, g, b)
        return {
            color.value.hex: color
            for color in Color.all()
        }.get(hex_.upper().strip("#"))

    @staticmethod
    def from_id(id_: int) -> 'Color':
        return {
            color.value.id: color
            for color in Color.all()
        }.get(id_)
