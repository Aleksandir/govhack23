#!/usr/bin/python3

import argparse
from shapely import from_geojson, to_geojson, GeometryCollection

BOUND_THRESHOLD = 0.1
SIMPLIFY_TOLERANCE = 1

def load_file(filename: str) -> str:
    with open(filename) as f:
        return f.read()

def large_enough(geom) -> bool:
    """Returns whether a geometry has some dimension bigger than BOUND_THRESHOLD."""
    bounds = geom.bounds
    return abs(bounds[2] - bounds[0]) >= BOUND_THRESHOLD or abs(bounds[3] - bounds[1]) >= BOUND_THRESHOLD

def simplify(geojson: str) -> str:
    geometry = from_geojson(geojson)
    # Filter out any geometries smaller than BOUND_THRESHOLD, and simplify remaining geometries.
    simplified = [g.simplify(SIMPLIFY_TOLERANCE) for g in geometry.geoms if large_enough(g)]
    return to_geojson(GeometryCollection(simplified))

parser = argparse.ArgumentParser()
parser.add_argument("filename", type=str, help="Filename of the input GeoJSON")
args = parser.parse_args()

print(simplify(load_file(args.filename)))
