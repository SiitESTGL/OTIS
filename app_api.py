import sqlalchemy
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from math import *

from models import POIS, Category, POIS_distances, User, API_Key, API_Log, Concelho, Images, Route, SequencePois
import json
from app_core import db, app, celery
from my_function_osrm import *
import fiona
from shapely.geometry import shape, Point
import shapefile
import time
import geopandas as gpd

from werkzeug.wrappers import Request, Response
from functools import wraps
from flask import Flask, jsonify, abort, make_response, request, url_for
from flask_limiter import Limiter

import ILS_testes_m_final_py3

#-----------------------------------------------------------------
#API Variables
#-----------------------------------------------------------------

use_limit = "100 per minute"

#-----------------------------------------------------------------
#API Status messages
#-----------------------------------------------------------------

arg_missing = "Please insert a category or concelho ID in your request."
query_success = "OK"
id_missing = "One of the IDs is invalid, please try another."
nothing_error = "Nothing was found, please try again."

#-----------------------------------------------------------------
#API Functions
#-----------------------------------------------------------------

#-----------------------------------------------------------------
#Get info about specific point by ID

def get_specific_poi_id(poi_id, task_id):
    
    #Query that grabs the requested POI from the database
    try:
        poi = POIS.query.get_or_404(poi_id)
    except:
        raise InvalidUsage(id_missing, status_code=404, task_id=task_id) 
    
    #Column that contains the dictionary keys
    column = ["id", "poi_name", "poi_lat", "poi_lon", "poi_categ", "poi_conc", "poi_descript", "images", "source"]
    info_poi =[];
    
    #Query to get the info from the category the POI belongs to 
    category = Category.query.get(int(poi.category_id)) 
    if category:
        categoryname = category.categ_name_pt
    else:
        categoryname = ""
    
    #Query to get the info from the concelho the POI belongs to
    if poi.concelho_id:
        concelho = Concelho.query.get(int(poi.concelho_id)) 
        if concelho:
            concelhoname = concelho.conc_name
        else:
            concelhoname = ""
    else:
        concelhoname = ""
    
    #Query to grab all the images that belong to the point    
    images_db =  db.session.query(Images.original_img).filter(Images.poi_id == poi.id).all() 
    
    #List that will store the image URLs
    images = [] 
    if images_db:
        for item2 in images_db:
            
            #Append the URLs to the list, allowing you to customize the address, for example to show 512px_ variants of images
            images.append( request.host_url + 'static/uploads/512px_'+ item2.original_img) 
    else:
        images = ""
    
    #Append the POI info for display as a list of dictionaries where the keys are in column and the values are the variables defined so far
    info_poi.append(dict(zip(column, [poi.id, poi.poi_name,
                                          poi.poi_lat, poi.poi_lon,
                                          categoryname,
                                          concelhoname,
                                          poi.poi_descri_pt_short,
                                          images,
                                          poi.poi_source])))
    
    return jsonify(result = info_poi, status = query_success, timestamp=time.time(), log_time=task_id)

#-----------------------------------------------------------------
#Get info on points belonging to a certain category

def get_specific_category(category, task_id):
    
    #Query that grabs POIs from the database based on if they match with the requested category id 
    poi = POIS.query.filter(POIS.category_id == category, POIS.poi_review == True).all()
    
    #Returns 404 if no pois are found
    if len(poi) == 0:
        raise InvalidUsage(nothing_error, task_id, status_code=404) 
    
    #Column that contains the dictionary keys
    column = ["id", "poi_name", "poi_lat", "poi_lon", "poi_categ", "poi_conc", "poi_descri_pt_short", "images", "source"]
    info_poi =[];
    
    #Grabs the category name from the requested category ID
    category = Category.query.get(category)
    if category:
        categoryname = category.categ_name_pt
    else:
        categoryname = ""
        
    #cycles the results of the POI query in order to build a list with the results
    for item in poi:
        
        #Grabs the concelho/municipality name from the POI's concelho ID
        if item.concelho_id:
            concelho = Concelho.query.get(int(item.concelho_id))
            if concelho:
                concelhoname = concelho.conc_name
            else:
                concelhoname = ""
        else:
            concelhoname = ""
            
        #Grabs all the images belonging to the POI    
        images_db =  db.session.query(Images.original_img).filter(Images.poi_id == item.id).all()
        images = []
        if images_db:
            for item2 in images_db:
                images.append( request.host_url + 'static/uploads/512px_'+ item2.original_img)
        else:
            images = ""
            
        #Appends the information from this POI to the list
        info_poi.append(dict(zip(column, [item.id, item.poi_name,
                                              item.poi_lat, item.poi_lon,
                                              categoryname,
                                              concelhoname,
                                              item.poi_descri_pt_short,
                                              images,
                                              item.poi_source])))
        
    return jsonify(result = info_poi, status = query_success, timestamp=time.time(), log_time=task_id)

#-----------------------------------------------------------------
#Get points belonging to a certain concelho

def get_specific_concelho(concelho, task_id):
    
    #Query that grabs POIs from the database based on if they match with the requested concelho id 
    poi = POIS.query.filter(POIS.concelho_id == concelho, POIS.poi_review == True).all()
    
    #Returns 404 if no pois are found
    if len(poi) == 0:
        raise InvalidUsage(nothing_error, status_code=404, task_id=task_id)
        
    #Column that contains the dictionary keys    
    column = ["id", "poi_name", "poi_lat", "poi_lon", "poi_categ", "poi_conc", "poi_descript", "images", "source"]
    info_poi =[];
    
    #Grabs the concelho name from the requested concelho ID
    concelho = Concelho.query.get(concelho)
    if concelho:
        concelhoname = concelho.conc_name
    else:
        concelhoname = ""
    
    #cycles the results of the POI query in order to build a list with the results
    for item in poi:
        
        #Grabs the category name from the POI's category ID
        category = Category.query.get(int(item.category_id))
        if category:
            categoryname = category.categ_name_pt
        else:
            categoryname = ""
        
        #Grabs all the images belonging to the POI
        images_db =  db.session.query(Images.original_img).filter(Images.poi_id == item.id).all()
        images = []
        if images_db:
            for item2 in images_db:
                images.append( request.host_url + 'static/uploads/512px_'+ item2.original_img)
        else:
            images = ""
            
        #Appends the information from this POI to the list
        info_poi.append(dict(zip(column, [item.id, item.poi_name,
                                              item.poi_lat, item.poi_lon,
                                              categoryname,
                                              concelhoname,
                                              item.poi_descri_pt_short,
                                              images,
                                              item.poi_source])))
    return jsonify(result = info_poi, status = query_success, timestamp=time.time(), log_time=task_id)

#-----------------------------------------------------------------
#Get points belonging to a certain category AND concelho

def get_specific_cat_conc(category, concelho, task_id):
    
    #Query that grabs POIs from the database based on if they match with the requested category ID and concelho ID
    poi = POIS.query.filter(POIS.category_id == category, POIS.concelho_id == concelho, POIS.poi_review == True).all()
    
    #Returns 404 if no POIs are found
    if len(poi) == 0:
        raise InvalidUsage(nothing_error, status_code=404, task_id=task_id)
        
    #Column that contains the dictionary keys
    column = ["id", "poi_name", "poi_lat", "poi_lon", "poi_categ", "poi_conc", "poi_descript", "images", "source"]
    info_poi =[];
    
    #Grabs the category and concelho/municipality names from the requested category ID and concelho ID
    category = Category.query.get(category)
    if category:
        categoryname = category.categ_name_pt
    else:
        categoryname = ""
    concelho = Concelho.query.get(concelho)
    if concelho:
        concelhoname = concelho.conc_name
    else:
        concelhoname = ""
        
    #cycles the results of the POI query in order to build a list with the results
    for item in poi:
        images_db =  db.session.query(Images.original_img).filter(Images.poi_id == item.id).all()
        images = []
        if images_db:
            for item2 in images_db:
                images.append( request.host_url + 'static/uploads/512px_'+ item2.original_img)
        else:
            images = ""
        info_poi.append(dict(zip(column, [item.id, item.poi_name,
                                              item.poi_lat, item.poi_lon,
                                              categoryname,
                                              concelhoname,
                                              item.poi_descri_pt_short,
                                              images,
                                              item.poi_source])))
    return jsonify(result = info_poi, status = query_success, timestamp=time.time(), log_time=task_id)

def calculate_poi_distance(in_lat, in_lon, poi):
    """
            Calculate the distance between two POIS based on Latitude and Longitude
        this function uses the "Haversine" formula to calculate the great circle between to POIS.
        Haversine Formula :  a = sin((lat2-lat1)/2)^2 + cos(lat1) * cos(lat2) * (sin(lon2 - lon 1))^2
            c = 2 * atan2(sqrt(a), sqrt(1-a))
           d = R * c, Where   R = hearth's radius(6371 km)
        :param in_lat: latitude type integer
        :param in_lon: longitude type integer
        :return:
        """
    lat1 = float(radians(in_lat))

    r = 6371  # in km
    lat2 = radians(float(poi.poi_lat))
    distan_lat = radians(lat2 - lat1)
    distan_lon = radians(float(poi.poi_lon - in_lon))
    a = (sin(distan_lat / 2)) ** 2 + cos(lat1) * cos(lat2) * (sin(distan_lon / 2)) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = r * c  # where  R is radius of the earth equal 6373 km & 3961 miles
    return distance
    
#-----------------------------------------------------------------
#Get points that are a certain distance from a pair of coordinates, can filter by category and/or concelho

def get_close_points(lat,lon,distance, task_id, category=None, concelho=None):
    # load shapefile containing Portugal's shape
    poly = gpd.read_file('static/shapefiles/portugal.shp')

    # construct point based on lon/lat returned by geocoder
    point = Point(lon, lat)

    # check each polygon to see if it contains the point
    if poly.contains(point).bool():    
        if category and concelho:
            poi = POIS.query.filter(POIS.category_id == category, POIS.concelho_id == concelho, POIS.poi_review == True).all()
        elif category:
            poi = POIS.query.filter(POIS.category_id == category, POIS.poi_review == True).all()
        elif concelho:
            poi = POIS.query.filter(POIS.concelho_id == concelho, POIS.poi_review == True).all()
        else:
            poi = POIS.query.filter(POIS.poi_review == True).all()

        column = ["id", "poi_name", "poi_lat", "poi_lon", "poi_categ", "poi_conc", "poi_descript", "Distance", "images", "source"]

        info_poi =[];
        for i,item in enumerate(poi):
            distance2 = calculate_poi_distance(lat, lon, item)
            if distance2 < distance:
                category = Category.query.get(int(item.category_id))
                if category:
                    categoryname = category.categ_name_pt
                else:
                    categoryname = ""
                if item.concelho_id:
                    concelho = Concelho.query.get(int(item.concelho_id))
                    if concelho:
                        concelhoname = concelho.conc_name
                    else:
                        concelhoname = ""
                else:
                    concelhoname = ""
                images_db =  db.session.query(Images.original_img).filter(Images.poi_id == item.id).all()
                images = []
                if images_db:
                    for item2 in images_db:
                        images.append( request.host_url + 'static/uploads/512px_'+ item2.original_img)
                else:
                    images = ""
                info_poi.append(dict(zip(column, [item.id, item.poi_name,
                                                      item.poi_lat, item.poi_lon,
                                                      categoryname,
                                                      concelhoname,
                                                      item.poi_descri_pt_short,
                                                      distance2,
                                                      images,
                                                      item.poi_source
                                                      ])))
        return jsonify(result = info_poi, status = query_success, timestamp=time.time(), log_time=task_id)
    raise InvalidUsage("Coordenates are outside the country's borders, please try another pair", status_code=400, task_id=task_id)    
        
#-----------------------------------------------------------------
#Get points that are a certain distance from a point called by ID, can filter by category and/or concelho

def get_close_points_id(poi_id, distance, task_id, category = None, concelho = None):
    
    # in case category and/or concelho exist, grab the points that match those parameters otherwise get all the POIs
    if category and concelho:
        poi = POIS.query.filter(POIS.category_id == category, POIS.concelho_id == concelho, POIS.poi_review == True).all()
    elif category:
        poi = POIS.query.filter(POIS.category_id == category, POIS.poi_review == True).all()
    elif concelho:
        poi = POIS.query.filter(POIS.concelho_id == concelho, POIS.poi_review == True).all()
    else:
        poi = POIS.query.filter(POIS.poi_review == True).all()
    if len(poi) == 0:
        raise InvalidUsage(nothing_error, status_code=404, task_id=task_id)
    
    
    column = ["id", "poi_name", "poi_lat", "poi_lon", "poi_categ", "poi_conc", "poi_descript", "images", "source"]
    info_poi =[];
    
    #query the POIS table for the requested POI so we can extract its latitude and longitude    
    try:
        poi2 = POIS.query.get_or_404(poi_id)
    except:
        raise InvalidUsage(id_missing, status_code=404, task_id=task_id) 
    lat = poi2.poi_lat
    lon = poi2.poi_lon
    
    #runs the calculate_pois_distance function defined above to calculate the distance between POIs
   
    #cycles the results of the POI query in order to build a list with the results
    for item in poi:
        distance2 = calculate_poi_distance(lat, lon, item)
        if distance2 < distance:
            category = Category.query.get(int(item.category_id))
            if category:
                categoryname = category.categ_name_pt
            else:
                categoryname = ""
            if item.concelho_id:
                concelho = Concelho.query.get(int(item.concelho_id))
                if concelho:
                    concelhoname = concelho.conc_name
                else:
                    concelhoname = ""
            else:
                concelhoname = ""
            images_db =  db.session.query(Images.original_img).filter(Images.poi_id == item.id).all()
            images = []
            if images_db:
                for item2 in images_db:
                    images.append( request.host_url + 'static/uploads/512px_'+ item2.original_img)
            else:
                images = ""
            info_poi.append(dict(zip(column, [item.id, item.poi_name,
                                                  item.poi_lat, item.poi_lon,
                                                  categoryname,
                                                  concelhoname,
                                                  item.poi_descri_pt_short,
                                                  images,
                                                  item.poi_source])))
        
    return jsonify(result = info_poi, status = query_success, timestamp=time.time(), log_time=task_id)


#-----------------------------------------------------------------
#Get points that are a certain travel time away from a point selected by ID, can filter by category and/or concelho and choose a
#profile (driving (default option) or walking)

def get_poi_trip_time(poi_id, time2, task_id, category2=None, concelho2=None, profile=None):
    
    #Query to get the distances of trips that start from the request point
    info = POIS_distances.query.filter(POIS_distances.start_poi_id==poi_id).all()
    
    if len(info) == 0:
        raise InvalidUsage(id_missing, status_code=404, task_id=task_id)
    
    column = ["id", "poi_name", "poi_lat", "poi_lon", "poi_categ", "poi_conc", "poi_descript", "trip_duration","images", "source"]
    info_poi=[];
    
    for item in info:
        
        #if check for the profile the user wants, defaults to "driving"
        
        if profile == "walking":
            
            #checks if the duration is below the requested one, if not the end POI is not processed and added to the result list
            if float(item.trip_duration_walk) < time2:
                
                #checks existance of category and concelho/municipality parameters in order to filter based on them
                if category2 and concelho2:
                    info2 = POIS.query.filter(POIS.id == item.end_poi_id, POIS.category_id == category2, POIS.concelho_id == concelho2, POIS.poi_review == True)
                elif category2:
                    info2 = POIS.query.filter(POIS.id == item.end_poi_id, POIS.category_id == category2, POIS.poi_review == True)
                elif concelho2:
                    info2 = POIS.query.filter(POIS.id == item.end_poi_id, POIS.concelho_id == concelho2, POIS.poi_review == True)
                else:
                    info2= POIS.query.filter(POIS.id == item.end_poi_id, POIS.poi_review == True)
                
                for item2 in info2:
                    category = Category.query.get(int(item2.category_id))
                    if category:
                        categoryname = category.categ_name_pt
                    else:
                        categoryname = ""
                    if item2.concelho_id:
                        concelho = Concelho.query.get(int(item2.concelho_id))
                        if concelho:
                            concelhoname = concelho.conc_name
                        else:
                            concelhoname = ""
                    else:
                        concelhoname = ""
                    images_db =  db.session.query(Images.original_img).filter(Images.poi_id == item2.id).all()
                    images = []
                    if images_db:
                        for item3 in images_db:
                            images.append( request.host_url + 'static/uploads/512px_'+ item3.original_img)
                    else:
                        images = ""
                    info_poi.append(dict(zip(column, [item2.id, item2.poi_name,
                                                          item2.poi_lat, item2.poi_lon,
                                                          categoryname,
                                                          concelhoname,
                                                          item2.poi_descri_pt_short,
                                                          item.trip_duration,
                                                          images,
                                                          item2.poi_source])))

        #default state that checks the trip duration based on the results from OSRM with the driving profile
        else:
            if float(item.trip_duration) < time2:
                if category2 and concelho2:
                    info2 = POIS.query.filter(POIS.id == item.end_poi_id, POIS.category_id == category2, POIS.concelho_id == concelho2, POIS.poi_review == True)
                elif category2:
                    info2 = POIS.query.filter(POIS.id == item.end_poi_id, POIS.category_id == category2, POIS.poi_review == True)
                elif concelho2:
                    info2 = POIS.query.filter(POIS.id == item.end_poi_id, POIS.concelho_id == concelho2, POIS.poi_review == True)
                else:
                    info2= POIS.query.filter(POIS.id == item.end_poi_id, POIS.poi_review == True)
                for item2 in info2:
                    category = Category.query.get(int(item2.category_id))
                    if category:
                        categoryname = category.categ_name_pt
                    else:
                        categoryname = ""
                    if item2.concelho_id:
                        concelho = Concelho.query.get(int(item2.concelho_id))
                        if concelho:
                            concelhoname = concelho.conc_name
                        else:
                            concelhoname = ""
                    else:
                        concelhoname = ""
                    images_db =  db.session.query(Images.original_img).filter(Images.poi_id == item2.id).all()
                    images = []
                    if images_db:
                        for item3 in images_db:
                            images.append( request.host_url + 'static/uploads/512px_'+ item3.original_img)
                    else:
                        images = ""
                    info_poi.append(dict(zip(column, [item2.id, item2.poi_name,
                                                          item2.poi_lat, item2.poi_lon,
                                                          categoryname,
                                                          concelhoname,
                                                          item2.poi_descri_pt_short,
                                                          item.trip_duration,
                                                          images,
                                                          item2.poi_source])))
    return jsonify(result = info_poi, status = query_success, timestamp=time.time(), log_time=task_id)

#-----------------------------------------------------------------
#Get points that are a certain travel time away from a set of coordinates, can filter by category and/or concelho and choose a
#profile (driving (default option) or walking)

def get_poi_trip_time2(lat, lon, time2, task_id, category=None, concelho=None, profile=None):

    # load shapefile containing Portugal's shape
    poly = gpd.read_file('static/shapefiles/portugal.shp')

    # construct point based on lon/lat returned by geocoder
    point = Point(lon, lat)

    # check each polygon to see if it contains the point
    if poly.contains(point).bool():  
            
        # in case category and/or concelho exist, grab the points that match those parameters otherwise get all the POIs
        if category and concelho:
            poi = POIS.query.filter(POIS.category_id == category, POIS.concelho_id == concelho, POIS.poi_review == True).all()
        elif category:
            poi = POIS.query.filter(POIS.category_id == category, POIS.poi_review == True).all()
        elif concelho:
            poi = POIS.query.filter(POIS.concelho_id == concelho, POIS.poi_review == True).all()
        else:
            #raise InvalidUsage(arg_missing, status_code=400)
            poi = POIS.query.filter(POIS.poi_review == True).all()
                
        column = ["id", "poi_name", "poi_lat", "poi_lon", "poi_categ", "poi_conc", "poi_descript", "trip_duration","images", "source"]
        info_poi=[];
            
        #iterates over the results of the query and depending on profile calculates the travel distance and time between the two
        for item in poi:
            
            #creates an upper-bond estimate to prematurely eliminate impossible points
            distance2 = calculate_poi_distance(lat, lon, item)
            if profile == "walking":
                duration2 = distance2/8*3600 #time taken to cover a distance at a speed of 8Km/h converted to seconds
            else:
                duration2 = distance2/70*3600 #time taken to cover a distance at a speed of 70Km/h converted to seconds    
            if duration2 <= time2:
                if profile == "walking":
                    distance, duration = get_trip_distance_duration_walk([lon, lat], [item.poi_lon, item.poi_lat])
                else:
                    distance, duration = get_trip_distance_duration([lon, lat], [item.poi_lon, item.poi_lat])

                #'if' check that validates whether the duration of the trip is below the requested one and if so adds that point's information to the result list
                if duration < time2:
                    category = Category.query.get(int(item.category_id))
                    if category:
                        categoryname = category.categ_name_pt
                    else:
                        categoryname = ""
                    if item.concelho_id:
                        concelho = Concelho.query.get(int(item.concelho_id))
                        if concelho:
                            concelhoname = concelho.conc_name
                        else:
                            concelhoname = ""
                    else:
                        concelhoname = ""
                    images_db =  db.session.query(Images.original_img).filter(Images.poi_id == item.id).all()
                    images = []
                    if images_db:
                        for item2 in images_db:
                            images.append( request.host_url + 'static/uploads/512px_'+ item2.original_img)
                    else:
                        images = ""

                    info_poi.append(dict(zip(column, [item.id, item.poi_name,
                                                              item.poi_lat, item.poi_lon,
                                                              categoryname,
                                                              concelhoname,
                                                              item.poi_descri_pt_short,
                                                              duration,
                                                              images,
                                                              item.poi_source])))
        return jsonify(result = info_poi, status = query_success, timestamp=time.time(), log_time=task_id)
    raise InvalidUsage("Coordenates are outside the country's borders, please try another pair", status_code=400, task_id=task_id)
    
#-----------------------------------------------------------------
#Function that calculates the best route when starting from a point defined by ID based on score and time spent on the point, number of days and max time for the trip. Also able to filter based on category and/or concelho
    
def route_calculator_id(m, duration, poi_id, start_time, task_id): #m = number of days, Tmax = max time   
    
    #Initialize all the data types that will be filled later
    O=[] #list that stores POI opening hours
    C=[] #list that stores POI closing hours
    T=[] #list that stores POI average visit duration time
    Score=[] #list that stores POI scores
    ids=() #tuple that stores POI IDs
    D=[] #Distance matrix
    Tmax = start_time+duration
    #query to get data relevant to the first point (the point the user requested the trip start from)
    try:
        poi2 = POIS.query.get_or_404(poi_id)
    except:
        raise InvalidUsage(id_missing, status_code=404, task_id=task_id)
    if poi2:
        item2 = poi2.poi_schedule.first()
        if item2:
            O.append(start_time)
            C.append(Tmax)
            T.append(0)
        ids= ids + (poi2.id,)
        
        #verification to make sure the score isn't 0
        if poi2.poi_score == 0:
            Score.append(1)
        else:
            Score.append(poi2.poi_score)
            
    poi = POIS.query.filter(POIS.id!= poi2.id, POIS.poi_review==1, POIS.category_id.in_([1, 2, 3, 6, 10])).all()
    
    #cycle that goes through the POIS query and allocates its data in accordance to the function's needs
    for item in poi:
        item2 = item.poi_schedule.first()
        if item2:
            O.append(item2.poi_open_h)
            C.append(item2.poi_close_h)
            T.append(item2.poi_vdura)
        ids= ids + (item.id,)
        if item.poi_score == 0:
            Score.append(1)
        else:
            Score.append(item.poi_score)

    n=len(T)

    #queries the distance between the points in order to build the distance matrix
    for i in range(0, len(ids)):  
        pois2=[]
        for row2 in db.engine.execute('SELECT trip_distance FROM pois_distances WHERE start_poi_id='+str(ids[i])+' AND end_poi_id IN'+str(ids)+''):
            pois2.append(row2[0])
        D.append(pois2) 

    for i in range(0,m):
        O.append(O[0]) #adds the arrival point
        C.append(C[0]) #adds the arrival point
        T.append(T[0])  #adds the arrival point     
        Score.append(0) #adds the arrival point
        ids = ids + (ids[0],)

    #Creates matrix for each day
    for i in range(0,n):
        for j in range(0,m): 
            D[i].append(D[0][i])

    for i in range(0,m): 
        D.append(D[0][:])
        
    #executes the function defined above to calculate the best round based on score and time spent
    besttour,bestfound=ILS_testes_m_final_py3.ILS_heuristic(m,Tmax,T,Score,O,C,D)
    
    info_poi =[];
    
    #iterates over the results of the previous function in order to build a result list with the data for all the points in the route
    for item in besttour[0]:
        poi = POIS.query.get_or_404(ids[item])
        column = ["id", "poi_name", "poi_lat", "poi_lon", "poi_categ", "poi_conc", "poi_descript", "images", "source"]

        category = Category.query.get(int(poi.category_id))
        if category:
            categoryname = category.categ_name_pt
        else:
            categoryname = ""
        if poi.concelho_id:
            concelho = Concelho.query.get(int(poi.concelho_id))
            if concelho:
                concelhoname = concelho.conc_name
            else:
                concelhoname = ""
        else:
            concelhoname = ""
        images_db =  db.session.query(Images.original_img).filter(Images.poi_id == poi.id).all()
        images = []
        if images_db:
            for item2 in images_db:
                images.append( request.host_url + 'static/uploads/512px_'+ item2.original_img)
        else:
            images = ""
        info_poi.append(dict(zip(column, [poi.id, poi.poi_name,
                                              poi.poi_lat, poi.poi_lon,
                                              categoryname,
                                              concelhoname,
                                              poi.poi_descri_pt_short,
                                              images,
                                              poi.poi_source])))

    return jsonify(result = info_poi, status = query_success, timestamp=time.time(), log_time=task_id)

#Function that calculates the best route when starting from a point defined by latitude and longitude based on score and time spent on the point, number of days and max time for the trip. Also able to filter based on category and/or concelho
    
def route_calculator_coord(m, Tmax, lat, lon, start_time, end_time, category, concelho, task_id): #m = number of days, Tmax = max time   
    
    #Initialize all the data types that will be filled later
    O=[] #list that stores POI opening hours
    C=[] #list that stores POI closing hours
    T=[] #list that stores POI average visit duration time
    Score=[] #list that stores POI scores
    ids=() #tuple that stores POI IDs
    D=[] #Distance matrix
    
    #append data relevant to the first point (the point the user requested the trip start from)
    O.append(start_time)
    C.append(end_time)
    T.append(0)
        
    #append initial score
    Score.append(1)
            
    poi = POIS.query.filter(POIS.poi_review==1, POIS.category_id.in_([1, 2, 3, 6, 10])).all()

    #cycle that goes through the POIS query and allocates its data in accordance to the function's needs
    for item in poi:
        item2 = item.poi_schedule.first()
        if item2:
            O.append(item2.poi_open_h)
            C.append(item2.poi_close_h)
            T.append(item2.poi_vdura)
        ids= ids + (item.id,)
        if item.poi_score == 0:
            Score.append(1)
        else:
            Score.append(item.poi_score)

    n=len(T)

    #builds the distance for the first point
    pois2=[0]
    for item in poi:
        distance, duration = get_trip_distance_duration([lon, lat], [item.poi_lon, item.poi_lat])
        pois2.append(distance)
    D.append(pois2)
    

    #queries the distance between the points in order to build the distance matrix
    for i in range(0, len(ids)):  
        pois2=[]
        for row2 in db.engine.execute('SELECT trip_distance FROM pois_distances WHERE start_poi_id='+str(ids[i])+' AND end_poi_id IN'+str(ids)+''):
            pois2.append(row2[0])
        D.append(pois2)
        
    for i, item in enumerate(poi, 1):
        distance, duration = get_trip_distance_duration([item.poi_lon, item.poi_lat], [lon, lat])
        D[i] = [distance] + D[i]

    for i in range(0,m):
        O.append(O[0]) #adds the arrival point
        C.append(C[0]) #adds the arrival point
        T.append(T[0])  #adds the arrival point     
        Score.append(0) #adds the arrival point
        #ids = ids + (ids[0],)

    #Creates matrix for each day
    for i in range(0,n):
        for j in range(0,m): 
            D[i].append(D[0][i])

    for i in range(0,m): 
        D.append(D[0][:])
        
    #executes the function defined above to calculate the best round based on score and time spent
    besttour,bestfound=ILS_testes_m_final_py3.ILS_heuristic(m,Tmax,T,Score,O,C,D)
    
    info_poi =[];
    besttour[0].pop() # removes final point since it's a generic point and thus not called by the program
    
    #iterates over the results of the previous function in order to build a result list with the data for all the points in the route
    for item in besttour[0]:
        poi = POIS.query.get_or_404(ids[item])
        column = ["id", "poi_name", "poi_lat", "poi_lon", "poi_categ", "poi_conc", "poi_descript", "images", "source"]

        category = Category.query.get(int(poi.category_id))
        if category:
            categoryname = category.categ_name_pt
        else:
            categoryname = ""
        if poi.concelho_id:
            concelho = Concelho.query.get(int(poi.concelho_id))
            if concelho:
                concelhoname = concelho.conc_name
            else:
                concelhoname = ""
        else:
            concelhoname = ""
        images_db =  db.session.query(Images.original_img).filter(Images.poi_id == poi.id).all()
        images = []
        if images_db:
            for item2 in images_db:
                images.append( request.host_url + 'static/uploads/512px_'+ item2.original_img)
        else:
            images = ""
        info_poi.append(dict(zip(column, [poi.id, poi.poi_name,
                                              poi.poi_lat, poi.poi_lon,
                                              categoryname,
                                              concelhoname,
                                              poi.poi_descri_pt_short,
                                              images,
                                              poi.poi_source])))

    return jsonify(result = info_poi, status = query_success, timestamp=time.time(), log_time=task_id)


#-----------------------------------------------------------------
#Get Distance, Duration and Polyline between two points using OSRM, accepts driving (default) and walking as its profiles
    
def get_OSRM_route_poitopoi(poi_id, poi_id2, task_id, profile=None):
    
    #gets the data from request points
    poi = POIS.query.get(poi_id)
    poi2 = POIS.query.get(poi_id2)
    
    #raise invalid usage if no point is returned from the POI ID query
    if poi is None or poi2 is None:
        raise InvalidUsage(id_missing, status_code=400, task_id=task_id)
        
    #calculates distance using the longitude and latitudes of both points and if the user asked for walking or driving
    if profile == "walking":
        distance, duration, geometry = get_trip_walking([poi.poi_lon, poi.poi_lat], [poi2.poi_lon, poi2.poi_lat])
    else:
        distance, duration, geometry = get_trip_driving([poi.poi_lon, poi.poi_lat], [poi2.poi_lon, poi2.poi_lat])
    return jsonify(distance = distance, duration = duration, geometry = geometry, status = query_success, timestamp=time.time(), log_time=task_id)

def get_OSRM_route_poitopoint(poi_id, lat, lon, task_id, profile=None, switch=0): #switch determines if it goes poi to point (0) or point to poi (1), default is poi to point
    # load shapefile containing Portugal's shape
    poly = gpd.read_file('static/shapefiles/portugal.shp')

    # construct point based on lon/lat returned by geocoder
    point = Point(lon, lat)

    # check each polygon to see if it contains the point
    if poly.contains(point).bool():  
        poi = POIS.query.get(poi_id)
        if poi is None:
            raise InvalidUsage(id_missing, status_code=400, task_id=task_id)
        if switch == 0:
            if profile == "walking":
                distance, duration, geometry = get_trip_walking([poi.poi_lon, poi.poi_lat], [lon, lat])
            else:
                distance, duration, geometry = get_trip_driving([poi.poi_lon, poi.poi_lat], [lon, lat])
        if switch == 1:
            if profile == "walking":
                distance, duration, geometry = get_trip_walking([lon, lat], [poi.poi_lon, poi.poi_lat])
            else:
                distance, duration, geometry = get_trip_driving([lon, lat], [poi.poi_lon, poi.poi_lat])

        return jsonify(distance = distance, duration = duration, geometry = geometry, status = query_success, timestamp=time.time(), log_time=task_id)
    raise InvalidUsage("Coordenates are outside the country's borders, please try another pair", status_code=400, task_id=task_id)
    
#-----------------------------------------------------------------    
#Get info about specific route by ID

def get_specific_route_id(route_id, task_id):
    
    #queries the DB for the route whose ID matches the request
    try:
        route = Route.query.get_or_404(route_id)
    except:
        raise InvalidUsage(id_missing, status_code=404, task_id=task_id) 
    
    column = ["id", "route_name", "travel_mode", "route_distance", "route_duration", "route_pois"]
    
    #grabs all the sequences of POIs belonging to the route requested
    q = db.session.query(SequencePois).filter(SequencePois.route_id == route_id).all()
    
    info_route = [];
    info_poi = [];
    column2 = ["id", "poi_name", "poi_lat", "poi_lon", "poi_categ", "poi_conc", "poi_descript", "images", "to_poi_descript", "source"]
    
    #iterates over the sequences to obtain the POIs belonging to the route and build a result list of POIs
    for item in q: 
        poi = db.session.query(POIS).filter(POIS.id == item.pois_list).first()
        if poi:
            category = Category.query.get(int(poi.category_id))
            if category:
                categoryname = category.categ_name_pt
            else:
                categoryname = ""
            if poi.concelho_id:
                concelho = Concelho.query.get(int(poi.concelho_id))
                if concelho:
                    concelhoname = concelho.conc_name
                else:
                    concelhoname = ""
            else:
                concelhoname = ""
            images_db =  db.session.query(Images.original_img).filter(Images.poi_id == poi.id).all()
            images = []
            if images_db:
                for item2 in images_db:
                    images.append( request.host_url + 'static/uploads/512px_512px_'+ item2.original_img)
            else:
                images = ""
            info_poi.append(dict(zip(column2, [poi.id, poi.poi_name,
                                                      poi.poi_lat, poi.poi_lon,
                                                      categoryname,
                                                      concelhoname,
                                                      poi.poi_descri_pt_short,
                                                      images,
                                                      item.descrip_start_end_pois_pt,
                                                      poi.poi_source])))
        
    info_route.append(dict(zip(column, [route.id, route.route_name,
                                                  route.mode_travel, route.route_distan,
                                                  route.route_duration,
                                                  info_poi])))
    
    return jsonify(result = info_route, status = query_success, timestamp=time.time(), log_time=task_id)

def get_apiauth_object_by_key(key):
    """
    Query the datastorage for an API key.
    @return: apiauth sqlachemy object.
    """
    return API_Key.query.filter_by(key=key).first()

def match_api_keys(key):
    """
    Match API keys
    @param key: API key from request
    @param ip: remote host IP to match the key.
    @return: boolean
    """
    if key is None:
        return False
    api_key = get_apiauth_object_by_key(key)
    if api_key is None:
        return False
    elif api_key.key == key:
        URL = request.url
        user = User.query.get_or_404(api_key.user_id)
        if user:
            
            #logs the API usage into the Database
            user_logs = API_Log(log_text = URL,
                                user_id = user.user_id,
                                log_ip = request.headers.get('X-Forwarded-For', request.remote_addr),
                                log_date=time.time())
            user.user_logs.append(user_logs)
            db.session.add(user)
            db.session.commit()
        return {'state':True, 'id': time.time()}
    return False


def require_app_key(f):
    """
    @param f: flask function
    @return: decorator, return the wrapped function or abort json object.
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        match = match_api_keys(request.args.get('key'))
        if match['state'] is True:
            return f(match['id'], *args, **kwargs)
        else:
            raise InvalidUsage('API Key invalid, please check if it is correct', status_code=401, task_id=task_id)
    return decorated

#-----------------------------------------------------------------
#Creates a template for error messages

class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, task_id, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload
        self.task_id = task_id

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        rv['status'] = self.status_code
        rv['timestamp'] = time.time()
        rv['log_time'] = self.task_id
        return rv
    
@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

#Error code 429 means ratelimit exceeded
@app.errorhandler(429)
def ratelimit_handler(e):
    return make_response(
            jsonify(error="ratelimit exceeded %s" % e.description, status_code=429)
            , 429
    )




#-----------------------------------------------------------------
#API use limit, shared for the API function

limiter = Limiter(
    app,
    key_func= lambda : request.args.get('key'),
    default_limits=["2 per minute", "1 per second"],
)
limiter.enabled = False
api_limit = limiter.shared_limit(use_limit, scope="mysql")


#-----------------------------------------------------------------
#API views
#-----------------------------------------------------------------

@app.route('/api/v1.0/poi_id', methods=['GET'])
@require_app_key
@api_limit
def get_poi_id(task_id):
    poi_id = int(request.args.get('id', None))
    task = get_specific_poi_id(poi_id, task_id)
    return task

@app.route('/api/v1.0/dist', methods=['GET']) 
@require_app_key
@api_limit
def get_task_close_point(task_id):
    lat  = float(request.args.get('lat', None))
    lon  = float(request.args.get('lon', None))
    dist = float(request.args.get('dist', None))
    cat = request.args.get('cat', None)
    conc = request.args.get('conc', None)
    task = get_close_points(lat, lon, dist, task_id, cat, conc )
    return task

@app.route('/api/v1.0/dist_id', methods=['GET']) 
@require_app_key
@api_limit
def get_task_close_point_2(task_id):
    poi_id  = int(request.args.get('id', None))
    dist = float(request.args.get('dist', None))
    cat = request.args.get('cat', None)
    conc = request.args.get('conc', None)
    task = get_close_points_id(poi_id, dist, task_id, cat, conc)
    return task

@app.route('/api/v1.0/poi_time', methods=['GET'])
@require_app_key
@api_limit
def get_task_close_time2(task_id):
    lat  = float(request.args.get('lat', None))
    lon  = float(request.args.get('lon', None))
    time = int(request.args.get('time', None))
    cat = request.args.get('cat', None)
    conc = request.args.get('conc', None)
    profile = request.args.get('profile', None)
    task = get_poi_trip_time2(lat, lon, time, task_id, cat, conc, profile)
    return task

@app.route('/api/v1.0/poi_time_id', methods=['GET'])
@require_app_key
@api_limit
def get_task_close_time(task_id):
    poi_id = int(request.args.get('id', None))
    cat = request.args.get('cat', None)
    conc = request.args.get('conc', None)
    time = int(request.args.get('time', None))
    profile = request.args.get('profile', None)
    task = get_poi_trip_time(poi_id, time, task_id, cat, conc, profile)
    return task

@app.route('/api/v1.0/poi', methods=['GET'])
@require_app_key
@api_limit
def get_specific_poi(task_id):
    cat = request.args.get('cat', None)
    conc = request.args.get('conc', None)
    if cat and conc:
        cat = int(cat)
        conc = int(conc)
        task = get_specific_cat_conc(cat, conc, task_id)
        return task
    if cat:
        cat = int(cat)
        task = get_specific_category(cat, task_id)
        return task
    if conc:
        conc = int(conc)
        task = get_specific_concelho(conc, task_id)
        return task
    raise InvalidUsage(arg_missing, task_id, status_code=400)
         
@app.route('/api/v1.0/route_calc_id', methods=['GET'])
@require_app_key
@api_limit
def route_calc_id(task_id):
    poi_id = int(request.args.get('id', None))
    start_time = int(request.args.get('start_time'))
    m = int(request.args.get('dias', None))
    duration = int(request.args.get('duration', None))
                            
    task = route_calculator_id(m, duration, poi_id, start_time, task_id)
    return task

@app.route('/api/v1.0/route_calc_coord', methods=['GET'])
@require_app_key
@api_limit
def route_calc_coord(task_id):
    lat  = float(request.args.get('lat', None))
    lon  = float(request.args.get('lon', None))
    start_time = int(request.args.get('start_time', None))
    end_time = int(request.args.get('end_time', None))
    cat = request.args.get('cat', None)
    conc = request.args.get('conc', None)
    m = int(request.args.get('dias', None))
    Tmax = int(request.args.get('tempo', None))
                            
    task = route_calculator_coord(m, Tmax, lat, lon, start_time, end_time, cat, conc, task_id)
    return task

@app.route('/api/v1.0/osrm_poipoi', methods=['GET'])
@require_app_key
@api_limit
def osrm_poipoi(task_id):
    poi_id = int(request.args.get('id', None))
    poi_id2 = int(request.args.get('id2', None))
    profile = request.args.get('profile', None)
    
    task = get_OSRM_route_poitopoi(poi_id, poi_id2, task_id, profile)
    
    return task

@app.route('/api/v1.0/osrm_poipoint', methods=['GET'])
@require_app_key
@api_limit
def osrm_poipoint(task_id):
    poi_id = int(request.args.get('id', None))
    lat  = float(request.args.get('lat', None))
    lon  = float(request.args.get('lon', None))
    profile = request.args.get('profile', None)
    
    task = get_OSRM_route_poitopoint(poi_id, lat, lon, task_id, profile, switch = 0)
    
    return task

@app.route('/api/v1.0/osrm_pointpoi', methods=['GET'])
@require_app_key
@api_limit
def osrm_pointpoi(task_id):
    poi_id = int(request.args.get('id', None))
    lat  = float(request.args.get('lat', None))
    lon  = float(request.args.get('lon', None))
    profile = request.args.get('profile', None)
    
    task = get_OSRM_route_poitopoint(poi_id, lat, lon, task_id, profile, switch = 1)
    
    return task

@app.route('/api/v1.0/route_id', methods=['GET'])
@require_app_key
@api_limit
def get_route_id(task_id):
    route_id = int(request.args.get('id', None))
    task = get_specific_route_id(route_id, task_id)
    return task