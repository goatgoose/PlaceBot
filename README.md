# PlaceBot

Draws to www.reddit.com/r/place.

## Usage
```python
from place_bot import Placer, Color

placer = Placer()
placer.login("username", "password")
placer.place_tile(432, 286, Color.BLACK)
```

See: [examples](examples/)

## Features
- place a tile at a coordinate
- maintain image 
   - diffs the canvas to a provided image and fills in the differing tiles
