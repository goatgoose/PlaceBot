# PlaceBot

Draws to www.reddit.com/r/place.

## Installation
```bash
pip install git+https://github.com/goatgoose/PlaceBot
```

## Usage
```python
from place_bot import Placer, Color

placer = Placer()
placer.login("username", "password")
placer.place_tile(432, 286, Color.BLACK)
```

See: [examples](examples/)

## Features / TODO
- [x] place a tile at a coordinate
- [x] maintain image
  - diffs the canvas to a provided image and fills in the differing tiles
- [ ] support for multiple reddit users
