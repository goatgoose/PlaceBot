class Color:
    def __init__(self, name: str, value: int, hex_: str):
        self.name = name
        self.value = value
        self.hex = hex_


def rgb2hex(r, g, b):
    return f"#{r:02x}{g:02x}{b:02x}"


colors_by_id = {
    1: Color("DARK_RED", 1, "BE0039"),
    2: Color("RED", 2, "FF4500"),
    3: Color("ORANGE", 3, "FFA800"),
    4: Color("YELLOW", 4, "FFD635"),
    6: Color("DARK_GREEN", 6, "00A368"),
    7: Color("GREEN", 7, "00CC78"),
    8: Color("LIGHT_GREEN", 8, "7EED56"),
    9: Color("DARK_TEAL", 9, "00756F"),
    10: Color("TEAL", 10, "009EAA"),
    12: Color("DARK_BLUE", 12, "2450A4"),
    13: Color("BLUE", 13, "3690EA"),
    14: Color("LIGHT_BLUE", 14, "51E9F4"),
    15: Color("INDIGO", 15, "493AC1"),
    16: Color("PERIWINKLE", 16, "6A5CFF"),
    18: Color("DARK_PURPLE", 18, "811E9F"),
    19: Color("PURPLE", 19, "B44AC0"),
    20: Color("PINK", 20, "FF3881"),
    23: Color("LIGHT_PINK", 23, "FF99AA"),
    25: Color("BROWN", 25, "6D482F"),
    26: Color("DARK_BROWN", 26, "9C6926"),
    27: Color("BLACK", 27, "000000"),
    29: Color("GRAY", 29, "898D90"),
    30: Color("LIGHT_GRAY", 30, "D4D7D9"),
    31: Color("WHITE", 31, "FFFFFF"),
}


colors_by_name = {c.name: c for c in colors_by_id.values()}

colors_by_hex = {c.hex: c for c in colors_by_id.values()}


def from_pixel(rgb_im_px) -> "Color":
    r, g, b = rgb_im_px
    hex_ = rgb2hex(r, g, b)
    return colors_by_hex[hex_.upper().strip("#")]


def from_name(name: str):
    return colors_by_name.get(name.upper())
