"""
Draw a map of my FBO network.
"""

from dataclasses import dataclass
from itertools import chain

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.basemap import Basemap

# https://python-graph-gallery.com/300-draw-a-connection-line
# https://python-graph-gallery.com/281-basic-map-with-basemap


@dataclass
class FBO:
    # icao: str
    name: str
    lat: float
    long: float
    owner: str
    lots: int
    runway_1: int
    runway_2: int = 0
    runway_3: int = 0
    elevation: int = 0
    ils: bool = False
    rnav: bool = False
    note: str = ""
    map_note: str = ""


# MAP_CORNERS = [20, -100, 70, 30]  # North Atlantic
# MAP_CORNERS = [35, -105, 42, -95]
MAP_CORNERS_OFFSET = 3
MAP_PROJECTION = "cyl"  # "merc"

LABEL_OFFSET = 0.1
FBO_SIZE = 9
FBO_COLOUR = "#69B3A2"

OCEAN_COLOUR = "#A6CAE0"
LAKE_COLOUR = OCEAN_COLOUR
RIVER_COLOUR = LAKE_COLOUR
LAND_COLOUR = "grey"  # '#e6b800'
COASTLINE_BORDERS = "white"
COUNTRY_BORDERS = "white"
STATE_BORDERS = "lightgrey"
CONNECTIONS_COLOUR = "orange"  # "#69B3A2"
CONNECTIONS_COLOUR_MINE = "orange"

OWNER_ME = "me!"
OWNER_RACAIR = "RacAir"
OWNER_NONE = "-"
FEET = 1
METERS = FEET * 3.28

fbos = {}

# fmt: off
fbos["1QK"] = FBO("Gove Co, aka 6KS1", 39+2.32/60, -1*(100+14.03/60), OWNER_ME, 1, 17, elevation=2637*FEET, rnav=True, map_note="old 6KS1")
fbos["98KS"] = FBO("Rexford", 37+26.97/60, -1*(100+30.39/60), OWNER_ME, 1, 18, elevation=2782*FEET)
fbos["SN29"] = FBO("Rucker", 38+11.16/60, -1*(99+32.13/60), OWNER_RACAIR, 3, 17, 3, 16, elevation=2151*FEET)
fbos["6KS1"] = FBO("Newman Regional Health Heliport", 38+24.64/60, -1*(96+11.73/60), OWNER_NONE, 1, 0, elevation=1164*FEET)
# fmt: on

connections = [
    ["1QK", "SN29"],
    ["98KS", "SN29"],
]

min_lat = min(x.lat for _, x in fbos.items())
min_long = min(x.long for _, x in fbos.items())
max_lat = max(x.lat for _, x in fbos.items())
max_long = max(x.long for _, x in fbos.items())

MAP_CORNERS = [
    min_lat - MAP_CORNERS_OFFSET,
    min_long - MAP_CORNERS_OFFSET,
    max_lat + MAP_CORNERS_OFFSET,
    max_long + MAP_CORNERS_OFFSET,
]

plt.rcParams["figure.figsize"] = 15, 12

## set up Basemap
m = Basemap(
    llcrnrlon=MAP_CORNERS[1],
    llcrnrlat=MAP_CORNERS[0],
    urcrnrlon=MAP_CORNERS[3],
    urcrnrlat=MAP_CORNERS[2],
    projection=MAP_PROJECTION,
)
m.drawmapboundary(fill_color=OCEAN_COLOUR, linewidth=0)

# Coastlines
m.fillcontinents(color=LAND_COLOUR, alpha=0.7, lake_color=LAKE_COLOUR)
m.drawcoastlines(linewidth=0.1, color=COASTLINE_BORDERS)
m.drawrivers(linewidth=0.1, color=RIVER_COLOUR)

# country color
m.drawcountries(color=COUNTRY_BORDERS, linewidth=1)

# Show states
m.drawstates(color=STATE_BORDERS, linewidth=1)

# startlat = 40.78
# startlon = -73.98
# arrlat = 51.53
# arrlon = 0.08
# m.drawgreatcircle(startlon, startlat, arrlon, arrlat, linewidth=2, color="orange")


for icao, fbo in fbos.items():
    label = f"{icao} ({fbo.map_note})" if fbo.map_note else icao
    print(f"{label} {fbo.lat:.2f}, {fbo.long:.2f}")
    plt.plot(fbo.long, fbo.lat, marker="o", markersize=FBO_SIZE, color=FBO_COLOUR)
    plt.annotate(
        label, xy=m(fbo.long + LABEL_OFFSET, fbo.lat), verticalalignment="center"
    )

print("***")

for start, end in connections:
    start_fbo = fbos[start]
    end_fbo = fbos[end]
    print(
        f"{start} - {end}; {start_fbo.lat:.2f}, {start_fbo.long:.2f} --> {end_fbo.lat:.2f}, {end_fbo.long:.2f}"
    )
    connection_color = (
        CONNECTIONS_COLOUR_MINE
        if (start_fbo.owner == OWNER_ME and end_fbo.owner == OWNER_ME)
        else CONNECTIONS_COLOUR
    )

    m.drawgreatcircle(
        start_fbo.long,
        start_fbo.lat,
        end_fbo.long,
        end_fbo.lat,
        linewidth=2,
        color=connection_color,
    )

# plt.show()
plt.savefig("fbo_network.png")
