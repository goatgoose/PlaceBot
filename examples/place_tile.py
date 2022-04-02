import sys
from place_bot import Placer, Color

if len(sys.argv) != 3:
    print("usage: python3 place_tile.py [reddit username] [reddit password]")
    exit()

username = sys.argv[1]
password = sys.argv[2]

placer = Placer()
placer.login(username, password)
placer.place_tile(432, 286, Color.BLACK)
