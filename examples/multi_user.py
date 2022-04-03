import json
from place_bot import Placer, Color

placer = Placer()

users = json.load(open("../testing/users.json", "r"))
for user in users:
    placer.login(user["username"], user["password"])

placer.maintain_image(1976, 882, "../testing/pink_square_rgb.png", (4, 4))
