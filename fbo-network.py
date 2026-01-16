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
OWNER_DAVYS747 = "Davys747"


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
    elevation: float = 0
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


def draw_fbo_network(fbos, connections, fn, annotation, annotation_location, figure_size):
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

    plt.rcParams["figure.figsize"] = figure_size[0], figure_size[1]

    ## set up Basemap
    m = Basemap(
        llcrnrlon=MAP_CORNERS[1],
        llcrnrlat=MAP_CORNERS[0],
        urcrnrlon=MAP_CORNERS[3],
        urcrnrlat=MAP_CORNERS[2],
        projection=MAP_PROJECTION,
    )
    # "paper" edge boundary
    m.drawmapboundary(fill_color=OCEAN_COLOUR, linewidth=0)

    # Coastlines
    m.fillcontinents(color=LAND_COLOUR, alpha=0.7, lake_color=LAKE_COLOUR)
    m.drawcoastlines(linewidth=0.1, color=COASTLINE_BORDERS)
    m.drawrivers(linewidth=0.5, color=RIVER_COLOUR)

    # country color
    m.drawcountries(color=COUNTRY_BORDERS, linewidth=1)

    # Show states
    m.drawstates(color=STATE_BORDERS, linewidth=1.5)

    # startlat = 40.78
    # startlon = -73.98
    # arrlat = 51.53
    # arrlon = 0.08
    # m.drawgreatcircle(startlon, startlat, arrlon, arrlat, linewidth=2, color="orange")
    
    plt.savefig(
        f"fbo_network_{fn}.png",  # bbox_inches="tight"
    )

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

        plt.savefig(
            f"fbo_network_{fn}.png",  # bbox_inches="tight"
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

    if annotation:
        plt.annotate(
            annotation,
            xy=annotation_location,
            xycoords="figure points",
            fontsize="x-large",
        )

    # plt.show()
    plt.savefig(
        f"fbo_network_{fn}.png",  # bbox_inches="tight"
    )

# fmt: off
fbo_1qk = FBO("Gove Co, aka 6KS1", 39+2.32/60, -1*(100+14.03/60), OWNER_ME, 1, 17, elevation=2637*FEET, rnav=True, map_note="old 6KS1")
fbo_98ks = FBO("Rexford", 37+26.97/60, -1*(100+30.39/60), OWNER_ME, 1, 18, elevation=2782*FEET)
fbo_sn29 = FBO("Rucker", 38+11.16/60, -1*(99+32.13/60), OWNER_RACAIR, 3, 17, 3, 16, elevation=2151*FEET)
fbo_6ks1 =  FBO("Newman Regional Health Heliport", 38+24.64/60, -1*(96+11.73/60), OWNER_NONE, 1, 0, elevation=1164*FEET)

# current FBOs
fbo_cfb6 = FBO("Josephberg", 53.7272, -113.086, OWNER_ME, 1, 8, elevation=2068*FEET, ils=False, rnav=False)
fbo_cee6 = FBO("Twin Island", 53.4711, -113.154, OWNER_ME, 1, 6, elevation=2434*FEET, ils=False, rnav=False)
fbo_cef4 = FBO("Aidrie", 51.2639, -113.935, OWNER_ME, 2, 12, elevation=3647*FEET, ils=False, rnav=False)
fbo_h28  = FBO("Whetstone/Del Bonita", 49.0000, -112.793, OWNER_ME, 2, 7, elevation=4335*FEET, ils=False, rnav=False)
fbo_cyba = FBO("Banff", 51.2, -115.533, OWNER_ME, 1, 18, elevation=4582*FEET, ils=False, rnav=False)

# former FBOs
fbo_cee8 = FBO("Viking", 53.1, -111.867, OWNER_NONE, 1, 13, elevation=2259*FEET)
fbo_cel6 = FBO("Two Hills", 53.7, -111.783, OWNER_NONE, 1, 12, elevation=2009*FEET)
fbo_cer2 = FBO("Castor", 52.2167, -111.933, OWNER_NONE, 1, 13, elevation=2703*FEET)

# surrounding reference FBOs
fbo_cyeg = FBO("Edmonton International", 53.3097, -113.58, OWNER_NONE, 3, 2, 12, elevation=2372*FEET, ils=True, rnav=True)
fbo_cyyc = FBO("Calgary International", 51.1139, -114.02, OWNER_NONE, 3, 17, 11, elevation=3556*FEET, ils=True, rnav=True)
fbo_cyql = FBO("Lethbridge", 49.6303, -112.8, OWNER_NONE, 3, 6, 13, elevation=3046*FEET)
fbo_kgtf = FBO("Great Falls", 47.482, -111.371, OWNER_NONE, 3, 3, 17, elevation=3676*FEET)
fbo_cybp = FBO("Brooks", 50.6336, -111.926, OWNER_DAVYS747, 2, 2, 12, elevation=2489*FEET)
fbo_ceg4 = FBO("Drumheller", 51.4964, -112.749, OWNER_DAVYS747, 2, 17, elevation=2598*FEET)
fbo_cef3 = FBO("Bow Island", 49.8833, -111.333, OWNER_DAVYS747, 1, 5, elevation=2633*FEET)
fbo_ced5 = FBO("Taber", 49.8267, -112.185, OWNER_NONE, 2, 5, 13,elevation=2647*FEET)
# fmt: on

def draw_ks_network():
    fbos_ks = {}
    fbos_ks["1QK"] = fbo_1qk
    fbos_ks["98KS"] = fbo_98ks
    fbos_ks["SN29"] = fbo_sn29
    fbos_ks["6KS1"] = fbo_6ks1

    connections_ks = [
        ["1QK", "SN29"],
        ["98KS", "SN29"],
    ]

    draw_fbo_network(
        fbos_ks,
        connections_ks, 
        "ks_2022-03-23", 
        "Cardboard GT's new FBO network (in red), 2022-03-23",
        (15, 25),
        (15, 12)
    )

def draw_ab_network():
    fbos_ab = {}
    fbos_ab["CFB6"] = fbo_cfb6
    fbos_ab["CEE6"] = fbo_cee6
    fbos_ab["CEF4"] = fbo_cef4
    fbos_ab["H28"] = fbo_h28
    fbos_ab["CYBA"] = fbo_cyba
    fbos_ab["CYEG"] = fbo_cyeg
    fbos_ab["CYYC"] = fbo_cyyc
    fbos_ab["CYQL"] = fbo_cyql
    # fbos_ab["KGTF"] = fbo_kgtf
    fbos_ab["CEE8"] = fbo_cee8
    fbos_ab["CEL6"] = fbo_cel6
    fbos_ab["CER2"] = fbo_cer2

    fbos_ab["CYBP"] = fbo_cybp
    fbos_ab["CEG4"] = fbo_ceg4
    fbos_ab["CEF3"] = fbo_cef3

    fbos_ab["CED5"] = fbo_ced5

    connections_ab = [
        ["CFB6", "CEF4"],
        ["CEF4", "H28"],
        ["CEF4", "CYBA"],
        # this connection breaks the mapping; is it too close together?
        # ["CEE6", "CFB6"],
    ]

    draw_fbo_network(
        fbos_ab,
        connections_ab, 
        "ab_2026-01-15",
        # None,
        "Cardboard GT's Alberta FBO network (in red), 2026-01-15",
        (18, 30),
        (10, 12.5),
    )

if __name__ == "__main__":
    # draw_ks_network()
    draw_ab_network()
