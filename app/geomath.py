import numpy as np
from haversine import haversine

# Conversion from and to latlon coordinate using https://stackoverflow.com/a/55256861
def convert_to_cartesian(coord):
    lat, lon = coord

    lat_rad = np.radians(lat)
    lon_rad = np.radians(lon)

    x = np.cos(lat_rad) * np.cos(lon_rad)
    y = np.cos(lat_rad) * np.sin(lon_rad)
    z = np.sin(lat_rad)

    return x, y, z

def convert_to_latlon(coord):
    x, y, z = coord

    lat_rad = np.arcsin(z)
    lon_rad = np.arctan2(y, x)

    lat = np.degrees(lat_rad)
    lon = np.degrees(lon_rad)

    return lat, lon

def calculate_intermediate_coordinates(coord1, coord2, num_points):
    x1, y1, z1 = convert_to_cartesian(coord1)
    x2, y2, z2 = convert_to_cartesian(coord2)

    dx = x2 - x1
    dy = y2 - y1
    dz = z2 - z1

    increment_x = dx / (num_points + 1)
    increment_y = dy / (num_points + 1)
    increment_z = dz / (num_points + 1)

    intermediate_coordinates = []
    for i in range(num_points):
        current_x = x1 + (increment_x * (i + 1))
        current_y = y1 + (increment_y * (i + 1))
        current_z = z1 + (increment_z * (i + 1))

        lat, lon = convert_to_latlon((current_x, current_y, current_z))
        intermediate_coordinates.append((lat, lon))

    return intermediate_coordinates

def calculate_coverage_percentage(start_coord, end_coord, current_coord):
    total_distance = haversine(start_coord, end_coord)
    covered_distance = haversine(start_coord, current_coord)
    return covered_distance / total_distance
