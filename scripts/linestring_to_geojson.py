#!/usr/bin/python3

import argparse
import re

"""Designed specifically to convert the geometries_2020.csv file to GeoJSON."""

def load_file(filename: str):
    with open(filename) as f:
        return f.readlines()

def to_geojson(lines):
    output = '{"type": "FeatureCollection", "features": [\n'
    pattern = re.compile('.*LINESTRING \((.*)\)')
    lines_printed = 0
    for line in lines:
        m = pattern.match(line)
        if m:
            if lines_printed == 0:
                output += '\n'
            else:
                output += ',\n'
            lines_printed += 1
            output += '{ "type": "Feature", "properties": {}, "geometry": { "type": "LineString", "coordinates": ['
            points = m.group(1).split(', ')
            for i, point in enumerate(points):
                lng, lat = point.split(' ')
                if i != 0:
                    output += ', '
                output += f'[{lng}, {lat}]'
            output += ']}}'
    output += ']}\n'
    return output

parser = argparse.ArgumentParser()
parser.add_argument("filename", type=str, help="Filename of the input CSV")
args = parser.parse_args()

print(to_geojson(load_file(args.filename)))
