"""
Draw a map of my FBO network.
"""

import math
from dataclasses import dataclass

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.basemap import Basemap  # pip install basemap

# https://python-graph-gallery.com/300-draw-a-connection-line
# https://python-graph-gallery.com/281-basic-map-with-basemap

EARTH_RADIUS = 6371  # in km
FEET = 1 / 3.28  # in meters
METERS = 1

# MAP_CORNERS = [20, -100, 70, 30]  # North Atlantic
# MAP_CORNERS = [35, -105, 42, -95]
MAP_CORNERS_OFFSET = 3
MAP_PROJECTION = "cyl"  # "merc"

LABEL_OFFSET = 0.15
FBO_SIZE = 12
FBO_COLOUR = "#69B3A2"
FBO_COLOUR_MINE = "red"

OCEAN_COLOUR = "#A6CAE0"
LAKE_COLOUR = OCEAN_COLOUR
RIVER_COLOUR = LAKE_COLOUR
LAND_COLOUR = "#eee"  # "grey"  # '#e6b800'
COASTLINE_BORDERS = "white"
COUNTRY_BORDERS = "white"
STATE_BORDERS = "lightgrey"
CONNECTIONS_COLOUR = "orange"  # "#69B3A2"
CONNECTIONS_COLOUR_MINE = "orange"
RUNWAY_COLOUR = "white"
RUNWAY_LENGTH = 30_000 * FEET

OWNER_ME = "me!"
OWNER_RACAIR = "RacAir"
OWNER_NONE = "-"


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


def runway_ends(lat, long, runway, length):
    """
    length in meters
    """
    # https://stackoverflow.com/a/69789709/4276230

    bearing_1 = runway * 10
    bearing_2 = runway * 10 + 180

    δ = (length / 2 / 1000) / EARTH_RADIUS

    φ0 = math.radians(lat)
    λ0 = math.radians(long)

    θ1 = math.radians(bearing_1)
    sinφ1 = math.sin(φ0) * math.cos(δ) + math.cos(φ0) * math.sin(δ) * math.cos(θ1)
    φ1 = math.asin(sinφ1)
    y1 = math.sin(θ1) * math.sin(δ) * math.cos(φ1)
    x1 = math.cos(δ) - math.sin(φ1) * sinφ1
    λ1 = λ0 + math.atan2(y1, x1)
    lat_1 = math.degrees(φ1)
    long_1 = math.degrees(λ1)

    θ2 = math.radians(bearing_2)
    sinφ2 = math.sin(φ0) * math.cos(δ) + math.cos(φ0) * math.sin(δ) * math.cos(θ2)
    φ2 = math.asin(sinφ2)
    y2 = math.sin(θ2) * math.sin(δ) * math.cos(φ2)
    x2 = math.cos(δ) - math.sin(φ2) * sinφ2
    λ2 = λ0 + math.atan2(y2, x2)
    lat_2 = math.degrees(φ2)
    long_2 = math.degrees(λ2)

    return [long_1, long_2], [lat_1, lat_2]


def draw_fbo_network(fbos, connections, fn, annotation):
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

    print("***")

    for icao, fbo in fbos.items():
        label = f"{icao} ({fbo.map_note})" if fbo.map_note else icao
        colour = FBO_COLOUR_MINE if fbo.owner == OWNER_ME else FBO_COLOUR
        print(
            f"{label} : {fbo.lat:.2f}, {fbo.long:.2f} : {fbo.runway_1} {fbo.runway_2} {fbo.runway_3}"
        )
        plt.plot(fbo.long, fbo.lat, marker="o", markersize=FBO_SIZE, color=colour)
        plt.annotate(
            label,
            xy=m(fbo.long + LABEL_OFFSET, fbo.lat),
            verticalalignment="center",
            fontsize="large",
        )
        if fbo.runway_1 != 0:
            runway = runway_ends(fbo.lat, fbo.long, fbo.runway_1, RUNWAY_LENGTH)
            print(f"    {runway}")
            plt.plot(
                *runway,
                linestyle="-",
                linewidth=2,
                color=RUNWAY_COLOUR,
            )
        if fbo.runway_2 != 0:
            runway = runway_ends(fbo.lat, fbo.long, fbo.runway_2, RUNWAY_LENGTH)
            print(f"    {runway}")
            plt.plot(
                *runway,
                linestyle="-",
                linewidth=2,
                color=RUNWAY_COLOUR,
            )
        if fbo.runway_3 != 0:
            runway = runway_ends(fbo.lat, fbo.long, fbo.runway_3, RUNWAY_LENGTH)
            print(f"    {runway}")
            plt.plot(
                *runway,
                linestyle="-",
                linewidth=2,
                color=RUNWAY_COLOUR,
            )

    plt.tight_layout()

    plt.annotate(
        annotation,
        xy=(15, 25),
        xycoords="figure points",
        fontsize="x-large",
    )

    # plt.show()
    plt.savefig(
        f"fbo_network_{fn}.png",  # bbox_inches="tight"
    )

def draw_ks_network():
    fbos_ks = {}

    # fmt: off
    fbos_ks["1QK"] = FBO("Gove Co, aka 6KS1", 39+2.32/60, -1*(100+14.03/60), OWNER_ME, 1, 17, elevation=2637*FEET, rnav=True, map_note="old 6KS1")
    fbos_ks["98KS"] = FBO("Rexford", 37+26.97/60, -1*(100+30.39/60), OWNER_ME, 1, 18, elevation=2782*FEET)
    fbos_ks["SN29"] = FBO("Rucker", 38+11.16/60, -1*(99+32.13/60), OWNER_RACAIR, 3, 17, 3, 16, elevation=2151*FEET)
    fbos_ks["6KS1"] = FBO("Newman Regional Health Heliport", 38+24.64/60, -1*(96+11.73/60), OWNER_NONE, 1, 0, elevation=1164*FEET)
    # fmt: on

    connections_ks = [
        ["1QK", "SN29"],
        ["98KS", "SN29"],
    ]

    draw_fbo_network(
        fbos_ks,
        connections_ks, 
        "ks_2022-03-23", 
        "Cardboard GT's new FBO network (in red), 2022-03-23"
    )

if __name__ == "__main__":
    draw_ks_network()
