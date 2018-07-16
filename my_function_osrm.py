__author__ = 'Jesus'

from python_osrm.osrm import *
from models import POIS
from flask import flash
from app_core import app

RequestConfig.host = app.config['OSRM_DRIVE_ADDRESS'] # mode driving using default config.
myconfig_bicyling = RequestConfig(app.config['OSRM_BIKE_ADDRESS']) # service for mode bicyling
myconfig_walking = RequestConfig(app.config['OSRM_WALK_ADDRESS']) #  service for mode walking


def get_trip_distance_duration(origin, destin):
    """
        Return trip distance and duration between two pois, by default mode of travel is driving
    """
    coord_start = [float(item) for item in origin]
    coord_finish = [float(item) for item in destin]

    distance = 0.0
    duration = 0.0
    r = simple_route(coord_start,coord_finish)
    if r:
        info_route = r['routes']
        for item in info_route:
            distance = item.get('distance')
            duration = item.get('duration')
    return (distance,duration)

def get_trip_driving(origin, destin):
    """
        Return trip data between two pois, by default mode of travel is driving
    """
    coord_start = [float(item) for item in origin]
    coord_finish = [float(item) for item in destin]

    distance = 0.0
    duration = 0.0
    r = simple_route(coord_start,coord_finish)
    if r:
        info_route = r['routes']
        for item in info_route:
            distance = item.get('distance')
            duration = item.get('duration')
            geometry = item.get('geometry')
    return (distance,duration,geometry)


def get_trip_distance_duration_walk(origin, destin):
    """
        Return trip distance and duration between two pois, by default mode of travel is walking
    """
    myconfig_walking = RequestConfig(app.config['OSRM_WALK_ADDRESS']) #  service for mode walking
    coord_start = [float(item) for item in origin]
    coord_finish = [float(item) for item in destin]

    distance = 0.0
    duration = 0.0
    r = simple_route(coord_start,coord_finish, url_config = myconfig_walking)
    if r:
        info_route = r['routes']
        for item in info_route:
            distance = item.get('distance')
            duration = item.get('duration')
    return (distance,duration)

def get_trip_walking(origin, destin):
    """
        Return trip data between two pois, by default mode of travel is driving
    """
    myconfig_walking = RequestConfig(app.config['OSRM_WALK_ADDRESS']) #  service for mode walking
    coord_start = [float(item) for item in origin]
    coord_finish = [float(item) for item in destin]

    distance = 0.0
    duration = 0.0
    r = simple_route(coord_start,coord_finish, url_config = myconfig_walking)
    if r:
        info_route = r['routes']
        for item in info_route:
            distance = item.get('distance')
            duration = item.get('duration')
            geometry = item.get('geometry')
    return (distance,duration, geometry)



def get_trip_duration(origin, destin):
    """
        Return trip duration between two pois,  by default mode of travel is driving
        :param origin: coordinate(longitude, latitdue)
        :param destin: coordinate of destin (longitude, latitude)
    """
    coord_start = [float(item) for item in origin]
    coord_finish = [float(item) for item in destin]
    duration = None
    r = simple_route(coord_start,coord_finish)
    info_route = r['routes']
    for item in info_route:
        duration = item.get('duration')
        break
    return duration

def get_trip_duration2(origin, destin):
    """
        Return trip duration between two pois, by default mode of travel is driving
    """
    coord_start = [float(item) for item in origin]
    coord_finish = [float(item) for item in destin]

    duration = 0.0
    r = simple_route(coord_start,coord_finish)
    if r:
        info_route = r['routes']
        for item in info_route:
            duration = item.get('duration')
    return duration

def get_route_distances(input_poi_id, modetravel):
    """
    :param input_poi_id:  poi id list
    :param modetravel: car, bicycle or foot
    :return: distance
    """
    start_poi = POIS.query.get(input_poi_id[0])
    end_poi = POIS.query.get(input_poi_id[len(input_poi_id)-1])

    coord_origin = []
    coord_destin = []
    coord_waypoints = []
    route_distance = None

    if start_poi:
        coord_origin.append(float(start_poi.poi_lon))
        coord_origin.append(float(start_poi.poi_lat ))

    if end_poi:
        coord_destin.append(float(end_poi.poi_lon))
        coord_destin.append(float(end_poi.poi_lat ))

    for index in range(1, len(input_poi_id)-1):
        coord_poi = POIS.query.get(input_poi_id[index])
        if coord_poi:
            coord_waypoints.append((coord_poi.poi_lon, coord_poi.poi_lat ))

    if modetravel == "driving":
        info_driving = simple_route(coord_origin,coord_destin,coord_intermediate= coord_waypoints)
        info_route = info_driving['routes']
        for item in info_route:
            route_distance = item.get('distance')
            break
    elif modetravel == "walking":
        info_walking = simple_route(coord_origin,coord_destin,coord_intermediate= coord_waypoints,url_config=myconfig_walking)
        info_route = info_walking['routes']
        for item in info_route:
            route_distance = item.get('distance')
            break
    elif modetravel == "bicycling":
        info_bicycling = simple_route(coord_origin,coord_destin,coord_intermediate= coord_waypoints,url_config=myconfig_bicyling)
        info_route = info_bicycling['routes']
        for item in info_route:
            route_distance = item.get('distance')
            break

    return route_distance


def get_route_duration(input_poi_id, modetravel):
    """
    :param input_poi_id :  poi id list
    :param modetravel: car, bycicle or foot
    :return: route duration
    """

    # Convert input value to float
    start_poi = POIS.query.get(input_poi_id[0])
    end_poi = POIS.query.get(input_poi_id[len(input_poi_id)-1])

    coord_origin = []
    coord_destin = []
    coord_waypoints = []
    route_duration = None

    if start_poi:
        coord_origin.append(float(start_poi.poi_lon))
        coord_origin.append(float(start_poi.poi_lat ))

    if end_poi:
        coord_destin.append(float(end_poi.poi_lon))
        coord_destin.append(float(end_poi.poi_lat ))

    for index in range(1, len(input_poi_id)-1):
        coord_poi = POIS.query.get(input_poi_id[index])
        if coord_poi:
            coord_waypoints.append((coord_poi.poi_lon, coord_poi.poi_lat ))

    if modetravel == "driving":
        info_driving = simple_route(coord_origin,coord_destin,coord_intermediate=coord_waypoints)
        info_route = info_driving['routes']
        for item in info_route:
            route_duration = item.get('duration')
            break
    elif modetravel == "walking":
        info_walking = simple_route(coord_origin,coord_destin,coord_intermediate= coord_waypoints,url_config=myconfig_walking)
        info_route = info_walking['routes']
        for item in info_route:
            route_duration = item.get('duration')
            break
    elif modetravel == "bicycling":
        info_bicycling = simple_route(coord_origin,coord_destin,coord_intermediate= coord_waypoints,url_config=myconfig_bicyling)
        info_route = info_bicycling['routes']
        for item in info_route:
            route_duration = item.get('duration')
            break
    return route_duration