from enum import Enum
from collections import namedtuple

import numpy as np

color = namedtuple("color", ["id", "hex"])


# https://stackoverflow.com/a/60748729
def static_init(cls):
    if getattr(cls, "static_init", None):
        cls.static_init()
    return cls


_PIXEL_MAP = None
_ID_MAP = None
_IDS_AND_RGB = None  # for fast numpy computations


@static_init
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

    @classmethod
    def static_init(cls):
        global _PIXEL_MAP
        _PIXEL_MAP = {
            color.value.hex: color
            for color in cls.all()
        }

        global _ID_MAP
        _ID_MAP = {
            color.value.id: color
            for color in cls.all()
        }
        global _IDS_AND_RGB
        _IDS_AND_RGB = np.asarray([
            [color.value.id, *cls.hex2rgb(color.value.hex)]
            for color in cls.all()
        ])

    @classmethod
    def all(cls):
        # https://stackoverflow.com/a/13286863
        return [
            getattr(cls, attr) for attr in dir(cls)
            if not callable(getattr(cls, attr))
            and not attr.startswith("__")
        ]

    @staticmethod
    def rgb2hex(r, g, b):
        return f"#{r:02x}{g:02x}{b:02x}"

    @staticmethod
    def hex2rgb(hex: str) -> list[int]:
        return [int(hex[2*i:2*i+2], base=16) for i in range(3)]

    @staticmethod
    def from_pixel(rgb_im_pix: list[int]) -> 'Color':
        color = Color.exact_from_pixel(rgb_im_pix)
        if color is None:
            color = Color.closest_from_pixel(rgb_im_pix)
        return color

    @staticmethod
    def exact_from_pixel(rgb_im_px: list[int]) -> 'Color':
        r, g, b = rgb_im_px
        hex_ = Color.rgb2hex(r, g, b)
        return _PIXEL_MAP.get(hex_.upper().strip("#"))

    @staticmethod
    def closest_from_pixel(rgb_im_pix: list[int]) -> 'Color':
        distances = np.linalg.norm(_IDS_AND_RGB[:,1:]-rgb_im_pix, axis=1)
        closest_i = np.argmin(distances)
        return Color.from_id(_IDS_AND_RGB[closest_i,0])

    @staticmethod
    def from_id(id_: int) -> 'Color':
        return _ID_MAP.get(id_)
