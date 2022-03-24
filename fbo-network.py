"""
Draw a map of my FBO network.
"""

from itertools import chain

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.basemap import Basemap

# https://python-graph-gallery.com/300-draw-a-connection-line
# https://python-graph-gallery.com/281-basic-map-with-basemap


my_fbos = [
    ["6KS1", 39.0706, -100.25, [0,]],
    ["98KS", 37.4459, -100.492],
]

other_fbos = [
    ["SN29", 38.1875, -99.534, None, "RacAir Headquarters"],
    ['"new" 6KS1', 38+24.64/60, -1*(96+11.73/60), None, "Newman Regional Health Heliport"],
]

# MAP_CORNERS = [20, -100, 70, 30]  # North Atlantic
MAP_CORNERS = [35, -105, 42, -95]
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


for fbo in chain(my_fbos, other_fbos):
    print(fbo[0], fbo[2], fbo[1])
    plt.plot(fbo[2], fbo[1], marker='o', markersize=FBO_SIZE, color=FBO_COLOUR)
    plt.annotate(
        fbo[0], xy=m(fbo[2] + LABEL_OFFSET, fbo[1]), verticalalignment="center"
    )

print("***")

for i in range(len(my_fbos)):
    fbo_0 = my_fbos[i]
    for j in range(len(my_fbos)):
        fbo_1 = my_fbos[j]
        if i < j:
            print(i, j, fbo_0[2], fbo_0[1], fbo_1[2], fbo_1[1])
            m.drawgreatcircle(
                fbo_0[2],
                fbo_0[1],
                fbo_1[2],
                fbo_1[1],
                linewidth=2,
                color=CONNECTIONS_COLOUR,
            )

# plt.show()
plt.savefig("fbo_network.png")
