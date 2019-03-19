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

import ILS_testes_m_final_cpy3 as ILS

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
#Get points belonging to a certain category AND concelho
def get_specific_cat_conc_b(category, concelho, task_id, num_poi=None, score=None):
    
    #Construct the query that grabs POIs from the database based on if they match with the requested category ID and concelho ID
    query_ini = 'SELECT pois.id, pois.poi_name, pois.poi_lat, pois.poi_lon, category.categ_name_pt, concelhos.conc_name, pois.poi_descri_pt_short, pois.poi_source FROM pois, category, concelhos'

    query_where = ' WHERE pois.category_id = category.categ_id AND pois.concelho_id = concelhos.conc_id'

    if category:
        query_where = query_where + ' AND pois.category_id = '+str(category)

    if concelho:
        query_where = query_where + ' AND pois.concelho_id = '+str(concelho)

    if score and int(score) > 0:
        query_where = query_where + ' AND pois.poi_score >= '+str(score)

    query_orderby = ' ORDER BY pois.poi_score DESC'

    if num_poi: query_limit = ' LIMIT '+str(num_poi)
    else: query_limit = ''

    query = query_ini+query_where+query_orderby+query_limit

    print(query)

    result = db.engine.execute(query).fetchall()

    if not result:
        raise InvalidUsage(nothing_error, status_code=404, task_id=task_id)

    #Column that contains the dictionary keys
    column = ["id", "poi_name", "poi_lat", "poi_lon", "poi_categ", "poi_conc", "poi_descript", "images", "source"]
    info_poi =[]

    #cycles the results of the POI query in order to build a list with the results
    for row in result:
        query_image = 'SELECT original_img FROM images WHERE poi_id = ' +str(row['id'])
        result_image = list(db.engine.execute(query_image).fetchall())
        images = []
        if result_image:
            for i in result_image:
                images.append( request.host_url + 'static/uploads/512px_'+ str(i[0]))
        else:
            images = ""
                    
        info_poi.append(dict(zip(column, [row['id'], row['poi_name'],
                                                  row['poi_lat'], row['poi_lon'],
                                                  row['categ_name_pt'],
                                                  row['conc_name'],
                                                  row['poi_descri_pt_short'],
                                                  images,
                                                  row['poi_source']
                                             ])))
    
    return jsonify(result = info_poi, status = query_success, timestamp=time.time(), log_time=task_id) 

#-----------------------------------------------------------------
def calculate_poi_distance_b(in_lat, in_lon, poi_lat, poi_lon):
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
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = radians(in_lon), radians(in_lat), radians(poi_lon), radians(poi_lat)   

    r = 6371  # in km
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    distance = r * c  # where  R is radius of the earth equal 6373 km & 3961 miles
    return distance
    
#-----------------------------------------------------------------
#Get points that are a certain distance from a pair of coordinates, can filter by category and/or concelho   
def get_close_points_b(lat, lon, distance, task_id, category=None, concelho=None, num_poi=None, order=None):
    # load shapefile containing Portugal's shape
    poly = gpd.read_file('static/shapefiles/portugal.shp')

    # construct point based on lon/lat returned by geocoder
    point = Point(lon, lat)

    # check each polygon to see if it contains the point
    if poly.contains(point).bool():    
    #if (lat < 42) and (lat > 37) and (lon > -9) and (lon < -6.1):

        query_ini = 'SELECT pois.id, pois.poi_name, pois.poi_lat, pois.poi_lon, category.categ_name_pt, concelhos.conc_name, pois.poi_descri_pt_short, pois.poi_source FROM pois, category, concelhos'

        query_where = ' WHERE pois.category_id = category.categ_id AND pois.concelho_id = concelhos.conc_id'

        if category:
            query_where = query_where + ' AND pois.category_id = '+str(category)

        if concelho:
            query_where = query_where + ' AND pois.concelho_id = '+str(concelho)

        if order == 'score': query_orderby = ' ORDER BY pois.poi_score DESC'
        else: query_orderby = ''

        query = query_ini+query_where+query_orderby
        result = db.engine.execute(query).fetchall()

        if not result:
            raise InvalidUsage(nothing_error, status_code=404, task_id=task_id)

        column = ["id", "poi_name", "poi_lat", "poi_lon", "poi_categ", "poi_conc", "poi_descript", "distance", "images", "source"]
        info_poi =[]

        for row in result:
            calc_distance = calculate_poi_distance_b(lat, lon, row['poi_lat'], row['poi_lon'])
            
            if calc_distance >= distance: continue
            else:
                query_image = 'SELECT original_img FROM images WHERE poi_id = ' +str(row['id'])
                result_image = list(db.engine.execute(query_image).fetchall())
                images = []
                if result_image:
                    for i in result_image:
                        images.append( request.host_url + 'static/uploads/512px_'+ str(i[0]))
                else:
                    images = ''
                    
                info_poi.append(dict(zip(column, [row['id'], row['poi_name'],
                                                          row['poi_lat'], row['poi_lon'],
                                                          row['categ_name_pt'],
                                                          row['conc_name'],
                                                          row['poi_descri_pt_short'],
                                                          calc_distance,
                                                          images,
                                                          row['poi_source']
                                                     ])))

        if not info_poi:
            raise InvalidUsage(nothing_error, status_code=404, task_id=task_id)

        #sort the result list by distance    
        if order == 'dist':
            info_poi = sorted(info_poi, key=lambda k: k['distance'])

        #select num_poi results from the result list    
        if num_poi:    
            info_poi = info_poi[:int(num_poi)]        

        return jsonify(result = info_poi, status = query_success, timestamp=time.time(), log_time=task_id)
    raise InvalidUsage("Coordenates are outside the country's borders, please try another pair", status_code=400, task_id=task_id)
        
#-----------------------------------------------------------------
#Get points that are a certain distance from a point called by ID, can filter by category and/or concelho
def get_close_points_id_b(poi_id, distance, task_id, category=None, concelho=None, num_poi=None, order=None):
    
    query_ini = 'SELECT pois.id, pois.poi_name, pois.poi_lat, pois.poi_lon, category.categ_name_pt, concelhos.conc_name, pois.poi_descri_pt_short, pois.poi_source FROM pois, category, concelhos'

    query_where = ' WHERE pois.category_id = category.categ_id AND pois.concelho_id = concelhos.conc_id'

    # in case category and/or concelho exist, add the contition to the query
    if category:
        query_where = query_where + ' AND pois.category_id = '+str(category)

    if concelho:
        query_where = query_where + ' AND pois.concelho_id = '+str(concelho)

    if order == 'score': query_orderby = ' ORDER BY pois.poi_score DESC'
    else: query_orderby = ''

    query = query_ini+query_where+query_orderby
    result = db.engine.execute(query).fetchall()

    if not result:
        raise InvalidUsage(nothing_error, status_code=404, task_id=task_id)
    
    #query the POIS table for the requested POI so we can extract its latitude and longitude 
    query_coord = 'SELECT poi_lat, poi_lon FROM pois WHERE id = ' +str(poi_id)
    result_coord = db.engine.execute(query_coord).fetchone()
    
    if not result_coord:
        raise InvalidUsage(nothing_error, status_code=404, task_id=task_id)
    
    poi_lat, poi_lon = result_coord
    
    column = ["id", "poi_name", "poi_lat", "poi_lon", "poi_categ", "poi_conc", "poi_descript", "images", "distance", "source"]
    info_poi =[]
    
    #cycles the results of the POI query in order to build a list with the results
    for row in result:
        #runs the calculate_pois_distance function defined above to calculate the distance between POIs
        calc_distance = calculate_poi_distance_b(poi_lat, poi_lon, row['poi_lat'], row['poi_lon'])
        
        if calc_distance >= distance: continue
        else:
            query_image = 'SELECT original_img FROM images WHERE poi_id = ' +str(row['id'])
            result_image = list(db.engine.execute(query_image).fetchall())
            images = []
            if result_image:
                for i in result_image:
                    images.append( request.host_url + 'static/uploads/512px_'+ str(i[0]))
            else:
                images = ""
            
            info_poi.append(dict(zip(column, [row['id'], row['poi_name'],
                                                      row['poi_lat'], row['poi_lon'],
                                                      row['categ_name_pt'],
                                                      row['conc_name'],
                                                      row['poi_descri_pt_short'],
                                                      images,
                                                      calc_distance,
                                                      row['poi_source']
                                                 ])))
    
    #sort the result list by distance
    if order == "dist":
        info_poi = sorted(info_poi, key=lambda k: k['distance'])
    
    #select num_poi results from the result list
    if num_poi:    
        info_poi = info_poi[:int(num_poi)]
    
    return jsonify(result = info_poi, status = query_success, timestamp=time.time(), log_time=task_id)

#-----------------------------------------------------------------
#Get points that are a certain travel time away from a point selected by ID, can filter by category and/or concelho and choose a
#profile (driving (default option) or walking)
def get_poi_trip_time_b(poi_id, time2, task_id, category=None, concelho=None, profile=None, num_poi=None, order=None):
    
    #Query to get the distances of trips that start from the request point
    query_ini = 'SELECT pois.id, pois.poi_name, pois.poi_lat, pois.poi_lon, category.categ_name_pt, concelhos.conc_name, pois.poi_descri_pt_short, pois.poi_source'

    query_from = ' FROM pois, category, concelhos, pois_distances'

    query_where = ' WHERE pois.category_id = category.categ_id AND pois.concelho_id = concelhos.conc_id AND pois.id = pois_distances.end_poi_id AND pois_distances.start_poi_id = ' +str(poi_id)

    #set the order of the query results, based on the user input
    if order == 'score':
        query_orderby = ' ORDER BY pois.poi_score DESC'
    elif order == 'time':
        query_orderby = ' ORDER BY pois_distances.trip_duration'
    elif order == 'dist':
        query_orderby = ' ORDER BY pois_distances.trip_distance'
    else:
        query_orderby = ''

    #checks existance of category and concelho/municipality parameters in order to filter based on them    
    if category:
        query_where = query_where + ' AND pois.category_id = '+str(category)

    if concelho:
        query_where = query_where + ' AND pois.concelho_id = '+str(concelho)

    #if check for the profile the user wants and add conditions to the query, defaults to "driving"
    #also add the condition to query the database about the trip duration, based on profile
    if profile == 'walking':
        query_ini = query_ini + ', pois_distances.trip_duration_walk AS trip_duration, pois_distances.trip_distance_walk AS trip_distance'
        query_where = query_where + ' AND pois_distances.trip_duration_walk <= ' +str(time2)
        if order and order != 'score': query_orderby = query_orderby + '_walk'
    else:
        query_ini = query_ini + ', pois_distances.trip_duration, pois_distances.trip_distance'
        query_where = query_where + ' AND pois_distances.trip_duration <= ' +str(time2)

    if order and order != 'score': query_orderby = query_orderby + ' ASC'

    #set the limit of results from the query, based on user inputs
    if num_poi: query_limit = ' LIMIT '+str(num_poi)
    else: query_limit = ''

    query = query_ini+query_from+query_where+query_orderby+query_limit
    result = db.engine.execute(query).fetchall()

    if not result:
        raise InvalidUsage(nothing_error, status_code=404, task_id=task_id)

    column = ["id", "poi_name", "poi_lat", "poi_lon", "poi_categ", "poi_conc", "poi_descript", "trip_duration","trip_distance","images", "source"]
    info_poi =[]

    for row in result:
        query_image = 'SELECT original_img FROM images WHERE poi_id = ' +str(row['id'])
        result_image = list(db.engine.execute(query_image).fetchall())
        images = []
        if result_image:
            for i in result_image:
                images.append( request.host_url + 'static/uploads/512px_'+ str(i[0]))
        else:
            images = ""
        
        info_poi.append(dict(zip(column, [row['id'], row['poi_name'],
                                                  row['poi_lat'], row['poi_lon'],
                                                  row['categ_name_pt'],
                                                  row['conc_name'],
                                                  row['poi_descri_pt_short'],
                                                  row['trip_duration'],
                                                  row['trip_distance'],
                                                  images,
                                                  row['poi_source']
                                             ])))
        
    return jsonify(result = info_poi, status = query_success, timestamp=time.time(), log_time=task_id)

#-----------------------------------------------------------------
#Get points that are a certain travel time away from a set of coordinates, can filter by category and/or concelho and choose a
#profile (driving (default option) or walking)
def get_poi_trip_time2_b(lat, lon, time2, task_id, num_poi=None, order=None, category=None, concelho=None, profile=None):
    
    # load shapefile containing Portugal's shape
    poly = gpd.read_file('static/shapefiles/portugal.shp')

    # construct point based on lon/lat returned by geocoder
    point = Point(lon, lat)
      
    # check each polygon to see if it contains the point
    if poly.contains(point).bool():
        
        query_ini = 'SELECT pois.id, pois.poi_name, pois.poi_lat, pois.poi_lon, category.categ_name_pt, concelhos.conc_name, pois.poi_descri_pt_short, pois.poi_source FROM pois, category, concelhos'

        query_where = ' WHERE pois.category_id = category.categ_id AND pois.concelho_id = concelhos.conc_id'

        if category:
            query_where = query_where + ' AND pois.category_id = '+str(category)

        if concelho:
            query_where = query_where + ' AND pois.concelho_id = '+str(concelho)

        if order == 'score': query_orderby = ' ORDER BY pois.poi_score DESC'
        else: query_orderby = ''
            
        query = query_ini+query_where+query_orderby
        result = db.engine.execute(query).fetchall()

        if not result:
            raise InvalidUsage(nothing_error, status_code=404, task_id=task_id)
            
        column = ["id", "poi_name", "poi_lat", "poi_lon", "poi_categ", "poi_conc", "poi_descript", "trip_duration","images", "source"]
        info_poi=[]
        
        #iterates over the results of the query and depending on profile calculates the travel distance and time between the two
        if profile == "walking":
            durations = get_trip_distance_duration_table_walk([(lon, lat)],[(float(row['poi_lon']),float(row['poi_lat'])) for row in result])
        else:
            duration = get_trip_distance_duration_table([(lon, lat)], [(float(row['poi_lon']),float(row['poi_lat'])) for row in result])
        
        for k,row in enumerate(result):
            #'if' check that validates whether the duration of the trip is below the requested one and if so adds that point's information to the result list
            if duration[k] >= time2: continue
            else:
                query_image = 'SELECT original_img FROM images WHERE poi_id = ' +str(row['id'])
                result_image = list(db.engine.execute(query_image).fetchall())
                images = []
                if result_image:
                    for i in result_image:
                        images.append( request.host_url + 'static/uploads/512px_'+ str(i[0]))
                else:
                    images = ""
                    
                info_poi.append(dict(zip(column, [row['id'], row['poi_name'],
                                                          row['poi_lat'], row['poi_lon'],
                                                          row['categ_name_pt'],
                                                          row['conc_name'],
                                                          row['poi_descri_pt_short'],
                                                          duration[k],
                                                          images,
                                                          row['poi_source']
                                                     ])))

        if not info_poi:
            raise InvalidUsage(nothing_error, status_code=404, task_id=task_id)

        #sort the result list by time
        if order == "time":
            info_poi = sorted(info_poi, key=lambda k: k['trip_duration'])

        #select num_poi results from the result list
        if num_poi:
            info_poi = info_poi[:int(num_poi)]

        return jsonify(result = info_poi, status = query_success, timestamp=time.time(), log_time=task_id)
    raise InvalidUsage("Coordenates are outside the country's borders, please try another pair", status_code=400, task_id=task_id)  
    
    
#-----------------------------------------------------------------
#Function that calculates the best route when starting from a point defined by ID based on score and time spent on the point, number of days and max time for the trip. Also able to filter based on category and/or concelho
    
def route_calculator_id(m, poi_id, start_time, duration, task_id): #m = number of days, Tmax = max time   
    
    #Initialize all the data types that will be filled later
    O=[]     #list that stores POI opening hours
    C=[]     #list that stores POI closing hours
    T=[]     #list that stores POI average visit duration time
    Score=[] #list that stores POI scores
    D=[]     #Distance matrix
    Tmax = start_time+duration

    #query to get data relevant to the first point (the point the user requested the trip start from)
    try:
        poi2 = POIS.query.get_or_404(poi_id)
    except:
        raise InvalidUsage(id_missing, status_code=404, task_id=task_id)
        
    if poi2:
        O.append(start_time)
        C.append(Tmax)
        T.append(0)
        Score.append(0)

    poi_list = db.engine.execute('SELECT id, poi_score FROM pois WHERE poi_review=1 AND category_id IN (1, 2, 3, 6, 10) AND id !='+ str(poi2.id)+' ORDER BY id ASC')
    
    ids_tuple = []
    dic_score = {}
    for row in poi_list:
        dic_score[row[0]] = row[1]  #tuple that stores POI scores
        ids_tuple.append(row[0])    #tuple that stores POI IDs

    ids_tuple = tuple(ids_tuple)
    
    res2 = db.engine.execute('SELECT poi_id,poi_open_h, poi_close_h, poi_vdura FROM pois_schedule WHERE poi_id IN'+str(ids_tuple)+' GROUP BY poi_id ORDER BY poi_id').fetchall()
    
    for row2 in res2:
        
        O.append(row2[1])
        C.append(row2[2])
        T.append(row2[3])
        if dic_score[row2[0]] == 0:
            Score.append(1)
        else:
            Score.append(dic_score[row2[0]])
            
    size=len(T)
    
    ids_tuple =  (poi2.id,) + ids_tuple

    #queries the distance between the points in order to build the distance matrix
    pois2=[]
    for row2 in db.engine.execute('SELECT trip_duration FROM pois_distances WHERE Start_POI_id IN'+str(ids_tuple)+' AND End_POI_id IN'+str(ids_tuple)+''):
        pois2.append(row2[0])

    D = [pois2[i:i+size] for i in range(0,len(pois2), size)]

    for i in range(0,m):
        O.append(O[0])  #adds the arrival point
        C.append(C[0])  #adds the arrival point
        T.append(T[0])  #adds the arrival point     
        Score.append(0) #adds the arrival point

       
    #Creates matrix for each day
    for i in range(0,size):
        for j in range(0,m): 
            D[i].append(D[0][i])

    for i in range(0,m): 
        D.append(D[0][:])
        
                
    #executes the function defined above to calculate the best round based on score and time spent
    besttour,bestfound=ILS.ILS_heuristic(m,Tmax,T,Score,O,C,D)
        
    ids_tuple = ids_tuple + (poi2.id,)
    
    day_list = {};
    #iterates over the results of the previous function in order to build a result list with the data for all the points in the route
    for d,tour in enumerate(besttour):
        info_poi =[];
        newlist = []
        for item in tour:
            newlist.append(ids_tuple[item])
            poi = POIS.query.get_or_404(ids_tuple[item])
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
        day_list["day_"+str(d+1)] = info_poi
    return jsonify(result = day_list, status = query_success, timestamp=time.time(), log_time=task_id,best=besttour[0],best2=newlist)

#-----------------------------------------------------------------
#Function that calculates the best route when starting from a point defined by ID based on score and time spent on the point, number of days and max time for the trip. Also able to filter based on category and/or concelho

def route_calculator_id2(m, poi_id, start_time, duration, task_id, category=None, concelho=None): #m = number of days, Tmax = max time   
    
    #Initialize all the data types that will be filled later
    O=[]     #list that stores POI opening hours
    C=[]     #list that stores POI closing hours
    T=[]     #list that stores POI average visit duration time
    Score=[] #list that stores POI scores
    D=[]     #Distance matrix
    Tmax = duration

    #query to get data relevant to the first point (the point the user requested the trip start from)
    try:
        poi2 = POIS.query.get_or_404(poi_id)
    except:
        raise InvalidUsage(id_missing, status_code=404, task_id=task_id)
        
    if poi2:
        O.append(start_time)
        C.append(Tmax)
        T.append(0)
        Score.append(0)
        
    if category is None:
        category = (1, 2, 3, 6, 10)

    if len(category) <= 2 and concelho == None:
            poi_list = db.engine.execute('SELECT id, poi_score FROM pois WHERE poi_review=1 AND category_id = '+ str(category) +' AND id !='+ str(poi2.id)+' ORDER BY id ASC')
    elif len(category) <= 2 and len(concelho) <= 2:
            poi_list = db.engine.execute('SELECT id, poi_score FROM pois WHERE poi_review=1 AND category_id = '+ str(category) +' AND concelho_id = '+ str(concelho) +' AND id !='+ str(poi2.id)+' ORDER BY id ASC')
    elif len(category) <= 2 and len(concelho) > 2:
            poi_list = db.engine.execute('SELECT id, poi_score FROM pois WHERE poi_review=1 AND category_id = '+ str(category) +' AND concelho_id IN '+ str(concelho) +' AND id !='+ str(poi2.id)+' ORDER BY id ASC')
    elif len(category) > 2 and len(concelho) > 2:
            poi_list = db.engine.execute('SELECT id, poi_score FROM pois WHERE poi_review=1 AND category_id IN '+ str(category) +' AND concelho_id IN '+ str(concelho) +' AND id !='+ str(poi2.id)+' ORDER BY id ASC')
    else:
            poi_list = db.engine.execute('SELECT id, poi_score FROM pois WHERE poi_review=1 AND category_id IN '+ str(category) +' AND id !='+ str(poi2.id)+' ORDER BY id ASC')
    
    ids_tuple = [] 
    dic_score = {}
    for row in poi_list:
        dic_score[row[0]] = row[1]  #tuple that stores POI scores
        ids_tuple.append(row[0])    #tuple that stores POI IDs

    if ids_tuple is None:
        return  jsonify(result = {'day_1':[]}, status = query_success, timestamp=time.time(), log_time=task_id)
    elif len(ids_tuple) == 1:
        res2 = db.engine.execute('SELECT poi_id,poi_open_h, poi_close_h, poi_vdura FROM pois_schedule WHERE poi_id ='+str(ids_tuple[0])+' GROUP BY poi_id ORDER BY poi_id').fetchall()
        ids_tuple = tuple(ids_tuple)
    else:    
        ids_tuple = tuple(ids_tuple)
        res2 = db.engine.execute('SELECT poi_id,poi_open_h, poi_close_h, poi_vdura FROM pois_schedule WHERE poi_id IN'+str(ids_tuple)+' GROUP BY poi_id ORDER BY poi_id').fetchall()
    
    for row2 in res2:
        
        O.append(row2[1]-start_time)
        C.append(row2[2]-start_time)
        T.append(row2[3])
        if dic_score[row2[0]] == 0:
            Score.append(1)
        else:
            Score.append(dic_score[row2[0]])
            
    size=len(T)
    
    ids_tuple =  (poi2.id,) + ids_tuple

    #queries the distance between the points in order to build the distance matrix
    pois2=[]
    
    if len(ids_tuple) == 1:
        for row2 in db.engine.execute('SELECT trip_duration FROM pois_distances WHERE Start_POI_id = '+str(ids_tuple[0])+' AND End_POI_id = '+str(ids_tuple[0])+''):
            pois2.append(row2[0])
    else:    
        for row2 in db.engine.execute('SELECT trip_duration FROM pois_distances WHERE Start_POI_id IN '+str(ids_tuple)+' AND End_POI_id IN '+str(ids_tuple)+''):
            pois2.append(row2[0])

    D = [pois2[i:i+size] for i in range(0,len(pois2), size)]

    for i in range(0,m):
        O.append(O[0])  #adds the arrival point
        C.append(C[0])  #adds the arrival point
        T.append(T[0])  #adds the arrival point     
        Score.append(0) #adds the arrival point

       
    #Creates matrix for each day
    for i in range(0,size):
        for j in range(0,m): 
            D[i].append(D[0][i])

    for i in range(0,m): 
        D.append(D[0][:])
        
                
    #executes the function defined above to calculate the best round based on score and time spent
    besttour,bestfound=ILS.ILS_heuristic(m,Tmax,T,Score,O,C,D)
        
    ids_tuple = ids_tuple + (poi2.id,)
    
    day_list = {};
    #iterates over the results of the previous function in order to build a result list with the data for all the points in the route
    for d,tour in enumerate(besttour):
        info_poi =[];
        newlist = []
        for item in tour:
            newlist.append(ids_tuple[item])
            poi = POIS.query.get_or_404(ids_tuple[item])
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
        day_list["day_"+str(d+1)] = info_poi
    return jsonify(result = day_list, status = query_success, timestamp=time.time(), log_time=task_id)
    
    
#Function that calculates the best route when starting from a point defined by latitude and longitude based on score and time spent on the point, number of days and max time for the trip. Also able to filter based on category and/or concelho
    
def route_calculator_coord(m, lat, lon, start_time, duration, task_id): #m = number of days, Tmax = max time   
# load shapefile containing Portugal's shape
    poly = gpd.read_file('static/shapefiles/portugal.shp')

    # construct point based on lon/lat returned by geocoder
    point = Point(lon, lat)

    # check each polygon to see if it contains the point
    if poly.contains(point).bool():    
        #Initialize all the data types that will be filled later
        O=[]     #list that stores POI opening hours
        C=[]     #list that stores POI closing hours
        T=[]     #list that stores POI average visit duration time
        Score=[] #list that stores POI scores
        D=[]     #Distance matrix
        Tmax = start_time+duration

        #append data relevant to the first point (the point the user requested the trip start from)
        O.append(start_time)
        C.append(Tmax)
        T.append(0)
        Score.append(0)

        poi_list = db.engine.execute('SELECT id, poi_score, poi_lat,poi_lon FROM pois WHERE poi_review=1 AND category_id IN(1, 2, 3, 6, 10) ORDER BY id ASC')

        
        ids_tuple = []
        dic_score = {}
        dest = []
        for row in poi_list:
            dic_score[row[0]] = row[1]  #tuple that stores POI scores
            ids_tuple.append(row[0])    #tuple that stores POI IDs
            dest.append((float(row[3]), float(row[2])) )
 
        ids_tuple = tuple(ids_tuple)

        res2 = db.engine.execute('SELECT poi_id,poi_open_h, poi_close_h, poi_vdura FROM pois_schedule WHERE poi_id IN'+str(ids_tuple)+' GROUP BY poi_id ORDER BY poi_id').fetchall()

        for row2 in res2:

            O.append(row2[1])
            C.append(row2[2])
            T.append(row2[3])
            if dic_score[row2[0]] == 0:
                Score.append(1)
            else:
                Score.append(dic_score[row2[0]])

        size=len(T)
        
        #queries the distance between the points in order to build the distance matrix
        durations_0j = get_trip_distance_duration_table_ger([(lon, lat)],dest)
        durations_j0 = get_trip_distance_duration_table_ger(dest,[(lon, lat)])

        durations_j0.insert(0,[0])
        
        pois2=[]
        for row2 in db.engine.execute('SELECT trip_duration FROM pois_distances WHERE Start_POI_id IN'+str(ids_tuple)+' AND End_POI_id IN'+str(ids_tuple)+''):
            pois2.append(row2[0])

        D = [pois2[i:i+size] for i in range(0,len(pois2), size-1)]

        D.insert(0, durations_0j[0])

        for k,row in enumerate(D):
            D[k] = durations_j0[k] + row

        #Creates matrix for each day
        for i in range(0,size):
            for j in range(0,m): 
                D[i].append(D[0][i])

        for i in range(0,m): 
            D.append(D[0][:])

        for i in range(0,m):
            O.append(O[0])  #adds the arrival point
            C.append(C[0])  #adds the arrival point
            T.append(T[0])  #adds the arrival point     
            Score.append(0) #adds the arrival point
        
        #executes the function defined above to calculate the best round based on score and time spent
        besttour,bestfound=ILS.ILS_heuristic(m,Tmax,T,Score,O,C,D)
        
        day_list = {};
        out = besttour[0].copy()
        #iterates over the results of the previous function in order to build a result list with the data for all the points in the route
        for d,tour in enumerate(besttour):
            tour.pop(0) # removes final point since it's a generic point and thus not called by the program
            tour.pop()  # removes final point since it's a generic point and thus not called by the program
            
            info_poi =[];
            newlist = []
            for item in tour:
                poi = POIS.query.get_or_404(ids_tuple[item-1])
                newlist.append(ids_tuple[item-1])
                
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
            day_list["day_"+str(d+1)] = info_poi
        return jsonify(result = day_list, status = query_success, timestamp=time.time(), log_time=task_id)
    raise InvalidUsage("Coordenates are outside the country's borders, please try another pair", status_code=400, task_id=task_id)    

def route_calculator_coord2(m, lat, lon, start_time, duration, task_id, category=None, concelho=None): #m = number of days, Tmax = max time   
# load shapefile containing Portugal's shape
    poly = gpd.read_file('static/shapefiles/portugal.shp')

    # construct point based on lon/lat returned by geocoder
    point = Point(lon, lat)

    # check each polygon to see if it contains the point
    if poly.contains(point).bool():    
        #Initialize all the data types that will be filled later
        O=[]     #list that stores POI opening hours
        C=[]     #list that stores POI closing hours
        T=[]     #list that stores POI average visit duration time
        Score=[] #list that stores POI scores
        D=[]     #Distance matrix
        Tmax = duration

        #append data relevant to the first point (the point the user requested the trip start from)
        O.append(0)
        C.append(Tmax)
        T.append(0)
        Score.append(0)

        if category == None:
            category = (1, 2, 3, 6, 10)

        if len(category) <= 2 and concelho == None:
            poi_list = db.engine.execute('SELECT id, poi_score, poi_lat,poi_lon  FROM pois WHERE poi_review=1 AND category_id = '+ str(category) +'ORDER BY id ASC')
        elif len(category) <= 2 and len(concelho) <= 2:
            poi_list = db.engine.execute('SELECT id, poi_score, poi_lat,poi_lon  FROM pois WHERE poi_review=1 AND category_id = '+ str(category) +' AND concelho_id = '+ str(concelho) +' ORDER BY id ASC')
        elif len(category) <= 2 and len(concelho) > 2:
            poi_list = db.engine.execute('SELECT id, poi_score, poi_lat,poi_lon  FROM pois WHERE poi_review=1 AND category_id = '+ str(category) +' AND concelho_id IN '+ str(concelho) +' ORDER BY id ASC')
        elif len(category) > 2 and len(concelho) > 2:
            poi_list = db.engine.execute('SELECT id, poi_score, poi_lat,poi_lon  FROM pois WHERE poi_review=1 AND category_id IN '+ str(category) +' AND concelho_id IN '+ str(concelho) +' ORDER BY id ASC')
        else:
            poi_list = db.engine.execute('SELECT id, poi_score, poi_lat,poi_lon FROM pois WHERE poi_review=1 AND category_id IN '+ str(category) +' ORDER BY id ASC')
        
        ids_tuple = []
        dic_score = {}
        dest = []
        for row in poi_list:
            dic_score[row[0]] = row[1]  #tuple that stores POI scores
            ids_tuple.append(row[0])    #tuple that stores POI IDs
            dest.append((float(row[3]), float(row[2])) )

        if ids_tuple is None:
            return  jsonify(result = {'day_1':[]}, status = query_success, timestamp=time.time(), log_time=task_id)
        elif len(ids_tuple) == 1:
            res2 = db.engine.execute('SELECT poi_id,poi_open_h, poi_close_h, poi_vdura FROM pois_schedule WHERE poi_id ='+str(ids_tuple[0])+' GROUP BY poi_id ORDER BY poi_id').fetchall()
            ids_tuple = tuple(ids_tuple)
            
            durations_0j = get_trip_distance_duration_table_ger([(lon, lat)],dest)
            durations_j0 = get_trip_distance_duration_table_ger(dest,[(lon, lat)])
            
            trip_time = durations_j0[0][0]+durations_0j[0][0]
            
            if float(trip_time) < Tmax:
                info_poi =[]
                newlist = []
                day_list = {}
                
                poi = POIS.query.get_or_404(ids_tuple[0])
                newlist.append(ids_tuple[0])
                
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
                
                day_list["day_1"] = info_poi
                return jsonify(result = day_list, status = query_success, timestamp=time.time(), log_time=task_id)
            else:
                return  jsonify(result = {'day_1':[]}, status = query_success, timestamp=time.time(), log_time=task_id)
            
        else:    
            ids_tuple = tuple(ids_tuple)
            res2 = db.engine.execute('SELECT poi_id,poi_open_h, poi_close_h, poi_vdura FROM pois_schedule WHERE poi_id IN'+str(ids_tuple)+' GROUP BY poi_id ORDER BY poi_id').fetchall()

        for row2 in res2:

            O.append(row2[1]-start_time)
            C.append(row2[2]-start_time)
            T.append(row2[3])
            if dic_score[row2[0]] == 0:
                Score.append(1)
            else:
                Score.append(dic_score[row2[0]])

        size=len(T)
        if size < 2:
            return  jsonify(result = {'day_1':[]}, status = query_success, timestamp=time.time(), log_time=task_id)
        
        #queries the distance between the points in order to build the distance matrix
        durations_0j = get_trip_distance_duration_table_ger([(lon, lat)],dest)
        durations_j0 = get_trip_distance_duration_table_ger(dest,[(lon, lat)])

        durations_j0.insert(0,[0])
        
        pois2=[]
           
        for row2 in db.engine.execute('SELECT trip_duration FROM pois_distances WHERE Start_POI_id IN '+str(ids_tuple)+' AND End_POI_id IN '+str(ids_tuple)+''):
            pois2.append(row2[0])

        D = [pois2[i:i+size] for i in range(0,len(pois2), size-1)]

        D.insert(0, durations_0j[0])

        for k,row in enumerate(D):
            D[k] = durations_j0[k] + row

        #Creates matrix for each day
        for i in range(0,size):
            for j in range(0,m): 
                D[i].append(D[0][i])

        for i in range(0,m): 
            D.append(D[0][:])

        for i in range(0,m):
            O.append(O[0])  #adds the arrival point
            C.append(C[0])  #adds the arrival point
            T.append(T[0])  #adds the arrival point     
            Score.append(0) #adds the arrival point
        
        #executes the function defined above to calculate the best round based on score and time spent
        besttour,bestfound=ILS.ILS_heuristic(m,Tmax,T,Score,O,C,D)
        
        day_list = {};
        out = besttour[0].copy()
        #iterates over the results of the previous function in order to build a result list with the data for all the points in the route
        for d,tour in enumerate(besttour):
            tour.pop(0) # removes final point since it's a generic point and thus not called by the program
            tour.pop()  # removes final point since it's a generic point and thus not called by the program
            
            info_poi =[];
            newlist = []
            for item in tour:
                poi = POIS.query.get_or_404(ids_tuple[item-1])
                newlist.append(ids_tuple[item-1])
                
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
            day_list["day_"+str(d+1)] = info_poi
        return jsonify(result = day_list, status = query_success, timestamp=time.time(), log_time=task_id)
    raise InvalidUsage("Coordenates are outside the country's borders, please try another pair", status_code=400, task_id=task_id)    
    
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
    num_poi = request.args.get('numpoi', None)
    order = request.args.get('order', None)
    task = get_close_points_b(lat, lon, dist, task_id, cat, conc, num_poi, order)
    return task

@app.route('/api/v1.0/dist_id', methods=['GET']) 
@require_app_key
@api_limit
def get_task_close_point_2(task_id):
    poi_id  = int(request.args.get('id', None))
    dist = float(request.args.get('dist', None))
    cat = request.args.get('cat', None)
    conc = request.args.get('conc', None)
    num_poi = request.args.get('numpoi', None)
    order = request.args.get('order', None)
    task = get_close_points_id_b(poi_id, dist, task_id, cat, conc, num_poi, order)
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
    num_poi = request.args.get('numpoi', None)
    order = request.args.get('order', None)
    #raise InvalidUsage('This view is gone', status_code=400, task_id=task_id)
    task = get_poi_trip_time2_b(lat, lon, time, task_id, num_poi, order, cat, conc, profile)
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
    num_poi = request.args.get('numpoi', None)
    order = request.args.get('order', None)
    #raise InvalidUsage('This view is gone', status_code=400)
    task = get_poi_trip_time_b(poi_id, time, task_id, cat, conc, profile, num_poi, order)
    return task

@app.route('/api/v1.0/poi', methods=['GET'])
@require_app_key
@api_limit
def get_specific_poi(task_id):
    cat = request.args.get('cat', None)
    conc = request.args.get('conc', None)
    num_poi = request.args.get('numpoi', None)
    score = request.args.get('score', None)
    task = get_specific_cat_conc_b(cat, conc, task_id, num_poi, score)
    return task
 
@app.route('/api/v1.0/route_calc_id', methods=['GET'])
@require_app_key
@api_limit
def route_calc_id(task_id):
    poi_id = int(request.args.get('id', None))
    start_time = int(request.args.get('start_time'))
    m = int(request.args.get('days', None))
    duration = int(request.args.get('duration', None))
                            
    task = route_calculator_id(m, poi_id, start_time, duration, task_id)
    return task

@app.route('/api/v1.0/route_calc_id2', methods=['GET'])
@require_app_key
@api_limit
def route_calc_id2(task_id):
    poi_id = int(request.args.get('id', None))
    start_time = int(request.args.get('start_time'))
    m = int(request.args.get('days', None))
    duration = int(request.args.get('duration', None))
    cat = str(request.args.get('cat', None))
    conc = str(request.args.get('conc', None))
                            
    task = route_calculator_id2(m, poi_id, start_time, duration, task_id, cat, conc)
    return task


@app.route('/api/v1.0/route_calc_coord', methods=['GET'])
@require_app_key
@api_limit
def route_calc_coord(task_id):
    lat  = float(request.args.get('lat', None))
    lon  = float(request.args.get('lon', None))
    start_time = int(request.args.get('start_time', None))
    duration = int(request.args.get('duration', None))
    m = int(request.args.get('days', None))                            
    task = route_calculator_coord(m, lat, lon,  start_time, duration, task_id)
    return task


@app.route('/api/v1.0/route_calc_coord2', methods=['GET'])
@require_app_key
@api_limit
def route_calc_coord2(task_id):
    lat  = float(request.args.get('lat', None))
    lon  = float(request.args.get('lon', None))
    start_time = int(request.args.get('start_time', None))
    duration = int(request.args.get('duration', None))
    m = int(request.args.get('days', None))
    cat = str(request.args.get('cat', None))
    conc = str(request.args.get('conc', None))
    
    task = route_calculator_coord2(m, lat, lon,  start_time, duration, task_id, cat, conc)
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