from models import *
from app_admin_function import is_number
from flask import redirect, flash, g

import json

inf = float("inf")

def decimal_second_to_hms(input_decimal):
        """
        Convert decimal second into HH:mm:ss
        :param input_decimal: insert number we want to convert
        :return: time format: ex- 12:02:05
        """
        if not is_number(input_decimal):
            time = False
        else:
            hour, rest = divmod(input_decimal, 3600)
            minute, second = divmod(rest, 60)
            time = "%02d:%02d" % (hour, minute)  # we just used Hour and Minutes
        return time
    
def decimal_second_to_hms2(input_decimal):
        if not is_number(input_decimal):
            time = False
        else:
            hour, rest = divmod(input_decimal, 3600)
            minute, second = divmod(rest, 60)
            time = "%02dh%02dm" % (hour, minute)  # we just used Hour and Minutes
        return time

# select all POI if categ_id == all, else select POI its category
def read_POIS_info(categ_id):
    poi_info = []
    if categ_id == "all":
        info = POIS.query.filter(POIS.poi_review==1)
        for item in info:
            poi_open_h2 = []
            poi_close_h2 = []
            poi_dura = []
            poi_phone = []
            poi_email = []
            poi_website = []
            poi_orig_img = []
            poi_copy_img = []
            
            category = ""
            category_id = None
            categ_info = Category.query.get(item.category_id)
            if categ_info:
                category = categ_info.categ_name_pt
                category_id = categ_info.categ_id
                
            concelho=""    
            conc_id = None
            conc_info = Concelho.query.get(item.concelho_id)
            if conc_info:
                concelho = conc_info.conc_name
                concelho_id = conc_info.conc_id
                
            for item2 in item.poi_schedule:
                poi_open_h_sec = item2.poi_open_h
                poi_open_h = decimal_second_to_hms(float(item2.poi_open_h))
                poi_close_h_sec = item2.poi_close_h
                poi_close_h = decimal_second_to_hms(item2.poi_close_h)
                POI_dura_sec = item2.poi_vdura
                poi_vdura = decimal_second_to_hms(item2.poi_vdura)
                poi_open_h2.append(poi_open_h)
                poi_close_h2.append(poi_close_h)
                if len (poi_dura)<1:
                    poi_dura.append(poi_vdura)
            
            for item2 in item.poi_contact:
                poi_phone.append(item2.telephone)
                poi_email.append(item2.email)
                poi_website.append(item2.website)
            
            for item2 in item.poi_image:
                poi_orig_img.append(item2.original_img)
                poi_copy_img.append(item2.copy_img)
            
            poi_info.append({
                "poi_id" : item.id,
                "poi_name": item.poi_name,
                "poi_lat": item.poi_lat,
                "poi_lon": item.poi_lon,
                "poi_category": category,
                "category_id": category_id,
                "poi_score": item.poi_score,
                "poi_concelho": concelho,
                "concelho_id": concelho_id,
                "poi_descript_pt": item.poi_descri_pt_short,
                "poi_descript_en": item.poi_descri_en_short,
                "address": item.poi_address,
                "poi_open_h_sec":poi_open_h_sec,
                "poi_open_h": poi_open_h2,
                "poi_close_h_sec": poi_close_h_sec,
                "poi_close_h": poi_close_h2,
                "poi_dura_sec": POI_dura_sec,
                "poi_dura": poi_dura,
                "poi_phone": poi_phone,
                "poi_email": poi_email,
                "poi_website": poi_website,
                "poi_orig_img": poi_orig_img,
                "poi_copy_img": poi_copy_img
            })
    else:
        info = POIS.query.with_entities(POIS).filter(POIS.category_id == categ_id)
        for item in info:
            category = ""
            category_id = None
            categ_info = Category.query.get(item.category_id)
            if categ_info:
                category = categ_info.categ_name_en
                category_id = categ_info.categ_id

            poi_info.append({
                "poi_name": item.poi_name,
                "poi_lat": item.poi_lat,
                "poi_lon": item.poi_lon,
                "poi_category": category,
                "category_id": category_id,
                "poi_descript_pt": item.poi_descri_pt_short
            })

    return json.dumps(poi_info)

def read_POIS_info2(categ_id):
    poi_info = []
    if categ_id == "all":
        info = POIS.query.filter(POIS.poi_review==1).order_by(POIS.poi_score.desc())
        for item in info:
            poi_open_h2 = []
            poi_close_h2 = []
            poi_dura = []
            poi_phone = []
            poi_email = []
            poi_website = []
            poi_orig_img = []
            poi_copy_img = []
            
            category = ""
            category_id = None
            categ_info = Category.query.get(item.category_id)
            if categ_info:
                category = categ_info.categ_name_pt
                category_id = categ_info.categ_id
                
            conc_id = None
            conc_info = Concelho.query.get(item.concelho_id)
            if conc_info:
                concelho = conc_info.conc_name
                concelho_id = conc_info.conc_id

            for item2 in item.poi_schedule:
                poi_open_h_sec = item2.poi_open_h
                poi_open_h = decimal_second_to_hms(float(item2.poi_open_h))
                poi_close_h_sec = item2.poi_close_h
                poi_close_h = decimal_second_to_hms(item2.poi_close_h)
                POI_dura_sec = item2.poi_vdura
                poi_vdura = decimal_second_to_hms(item2.poi_vdura)
                poi_open_h2.append(poi_open_h)
                poi_close_h2.append(poi_close_h)
                if len (poi_dura)<1:
                    poi_dura.append(poi_vdura)
            
            for item2 in item.poi_contact:
                poi_phone.append(item2.telephone)
                poi_email.append(item2.email)
                poi_website.append(item2.website)
            
            for item2 in item.poi_image:
                poi_orig_img.append(item2.original_img)
                poi_copy_img.append(item2.copy_img)
            
            poi_info.append({
                "poi_id" : item.id,
                "poi_name": item.poi_name,
                "poi_lat": item.poi_lat,
                "poi_lon": item.poi_lon,
                "poi_category": category,
                "category_id": category_id,
                "poi_score": item.poi_score,
                "poi_concelho": concelho,
                "concelho_id": concelho_id,
                "poi_descript_pt": item.poi_descri_pt_short,
                "poi_descript_en": item.poi_descri_en_short,
                "address": item.poi_address,
                "poi_open_h_sec":poi_open_h_sec,
                "poi_open_h": poi_open_h2,
                "poi_close_h_sec": poi_close_h_sec,
                "poi_close_h": poi_close_h2,
                "poi_dura_sec": POI_dura_sec,
                "poi_dura": poi_dura,
                "poi_phone": poi_phone,
                "poi_email": poi_email,
                "poi_website": poi_website,
                "poi_orig_img": poi_orig_img,
                "poi_copy_img": poi_copy_img
            })
    else:
        info = POIS.query.with_entities(POIS).filter(POIS.category_id == categ_id)
        for item in info:
            category = ""
            category_id = None
            categ_info = Category.query.get(item.category_id)
            if categ_info:
                category = categ_info.categ_name_en
                category_id = categ_info.categ_id

            poi_info.append({
                "poi_name": item.poi_name,
                "poi_lat": item.poi_lat,
                "poi_lon": item.poi_lon,
                "poi_category": category,
                "category_id": category_id,
                "poi_descript_pt": item.poi_descri_pt_short
            })

    return json.dumps(poi_info)

# select all POI if categ_id == all, else select POI its category, regardless of whether the POI is finished
def read_POIS_info3(categ_id):
    poi_info = []
    if categ_id == "all":

        info = POIS.query.order_by(POIS.poi_score.desc()).all()

        for item in info:
            poi_open_h2 = []
            poi_close_h2 = []
            poi_dura = []
            poi_phone = []
            poi_email = []
            poi_website = []
            poi_orig_img = []
            poi_copy_img = []
            
            if item.category_id:
                categ_info = Category.query.get(item.category_id)
                category = categ_info.categ_name_pt
                category_id = categ_info.categ_id
            else:
                category_id = 11
                categ_info = Category.query.get(category_id)
                category = categ_info.categ_name_pt
                
            if item.concelho_id:
                conc_info = Concelho.query.get(item.concelho_id)
                concelho = conc_info.conc_name
                concelho_id = conc_info.conc_id     
            else:
                concelho_id = 20
                conc_info = Concelho.query.get(concelho_id)
                concelho = conc_info.conc_name

            for item2 in item.poi_schedule:
                poi_open_h_sec = item2.poi_open_h
                poi_open_h = decimal_second_to_hms(float(item2.poi_open_h))
                poi_close_h_sec = item2.poi_close_h
                poi_close_h = decimal_second_to_hms(item2.poi_close_h)
                POI_dura_sec = item2.poi_vdura
                poi_vdura = decimal_second_to_hms(item2.poi_vdura)
                poi_open_h2.append(poi_open_h)
                poi_close_h2.append(poi_close_h)
                if len (poi_dura)<1:
                    poi_dura.append(poi_vdura)
            
            for item2 in item.poi_contact:
                poi_phone.append(item2.telephone)
                poi_email.append(item2.email)
                poi_website.append(item2.website)
            
            for item2 in item.poi_image:
                poi_orig_img.append(item2.original_img)
                poi_copy_img.append(item2.copy_img)
            
            poi_info.append({
                "poi_id" : item.id,
                "poi_name": item.poi_name,
                "poi_lat": item.poi_lat,
                "poi_lon": item.poi_lon,
                "poi_category": category,
                "category_id": category_id,
                "poi_score": item.poi_score,
                "poi_concelho": concelho,
                "concelho_id": concelho_id,
                "poi_descript_pt": item.poi_descri_pt_short,
                "poi_descript_en": item.poi_descri_en_short,
                "address": item.poi_address,
                "poi_open_h_sec":poi_open_h_sec,
                "poi_open_h": poi_open_h2,
                "poi_close_h_sec": poi_close_h_sec,
                "poi_close_h": poi_close_h2,
                "poi_dura_sec": POI_dura_sec,
                "poi_dura": poi_dura,
                "poi_phone": poi_phone,
                "poi_email": poi_email,
                "poi_website": poi_website,
                "poi_orig_img": poi_orig_img,
                "poi_copy_img": poi_copy_img,
                "poi_review": item.poi_review
            })
    else:
        info = POIS.query.with_entities(POIS).filter(POIS.category_id == categ_id)
        for item in info:
            category = ""
            category_id = None
            categ_info = Category.query.get(item.category_id)
            if categ_info:
                category = categ_info.categ_name_en
                category_id = categ_info.categ_id
            flash("neste")
            poi_info.append({
                "poi_name": item.poi_name,
                "poi_lat": item.poi_lat,
                "poi_lon": item.poi_lon,
                "poi_category": category,
                "category_id": category_id,
                "poi_descript_pt": item.poi_descri_pt_short,
                "poi_review": item.poi_review
            })

    return json.dumps(poi_info)

#Function to read the DB for route info and return it

def read_route_info():
    route_info = []

    info = Route.query.all()
    for item in info:
        
        duration_hm = decimal_second_to_hms2(item.route_duration) 
        
        q = db.session.query(SequencePois).filter(SequencePois.route_id == item.id).first()
        
        if q:
            poi = db.session.query(POIS).filter(POIS.id == q.pois_list).first()
            if poi:
                lat = poi.poi_lat
                lon = poi.poi_lon
                poi_name = poi.poi_name
            
        route_info.append({
            "route_id" : item.id,
            "route_name": item.route_name,
            "mode_travel": item.mode_travel,
            "route_descript": item.route_descrip_pt,
            "route_distance": item.route_distan,
            "route_duration": duration_hm,
            "start_poi": poi_name,
            "start_lat": lat,
            "start_lon": lon
        })
    return json.dumps(route_info)


# return the IDs of POIs that fit the time table of the route
def duration_check(poi_id, duration, current_pois, return_time, curr_time, wtl):
    newlist = list(current_pois); #creates parallel list to current valid POIs list which will be returned
    j = 0

    for i in range(0, len(current_pois)):
        valid1 = 1
        info = POIS_distances.query.filter(POIS_distances.start_poi_id==poi_id).filter(POIS_distances.end_poi_id==int(current_pois[i]['id'])) #grabs distance and duration where start is the selected point and end point is one of the current visible points

        for item in info:

            wait_time = max(0, (int(current_pois[i]['start_time']) - float(curr_time) - item.trip_duration)) #Determines the time the user will have to wait upon reaching the point

            triptime = item.trip_duration + int(current_pois[i]['dura']) + wait_time
            if (float(curr_time) + triptime) > int(current_pois[i]['end_time']):
                valid1 = 0
            
            if (valid1 == 1):
                durdif = float(duration) - triptime #calculates difference between current duration and POI's trip duration + visit duration
                durdif -= current_pois[i]['return_time']
                if durdif < 0: #or wait_time > int(wtl) : # if POI is not valid, removes it from list, otherwise increment j to continue across the list. Wait time is in seconds, 1800 seconds = 30 minutes
                    newlist.pop(j) 
                else:
                    newlist[j]['travel_time'] = triptime
                    j += 1
            else:
                newlist.pop(j)
    
    return json.dumps(newlist)

def route_poi_duration(route_pois):
    length = len(route_pois)
    poi_dur = POIS_distances.query.filter(POIS_distances.start_poi_id==int(route_pois[length-2]['id'])).filter(POIS_distances.end_poi_id==int(route_pois[length-1]['id']))
    for item in poi_dur:
        
        tduration = item.trip_duration + int(route_pois[length-1]['dura']) 
    return json.dumps(tduration) # return trip time + visit duration of selected point

#make sure the first element of route_pois already has its travel_time defined
#function re-calculates the time spent on each point in the route
def route_poi_duration2(route_pois, current_time, finish_time):
    length = len(route_pois)
    float_current_time = float(current_time)
    for item in range (1, length):
        poi_dur = POIS_distances.query.filter(POIS_distances.start_poi_id==int(route_pois[item-1]['id'])).filter(POIS_distances.end_poi_id==int(route_pois[item]['id']))
        
        for item2 in poi_dur:
            wait_time = max(0, (int(route_pois[item]['start_time']) - float(current_time) - item2.trip_duration))
            tduration = item2.trip_duration + int(route_pois[item]['dura']) + wait_time
            route_pois[item]['travel_time'] = tduration
            float_current_time += tduration
            if (item == length):
                if (float_current_time > float(route_pois[item]['end_time'])) or ((float_current_time+float(route_pois[item]['return_time'])) > float(finish_time)):
                    route_pois[item]['validity'] = 0 #0 if point is now invalid
                else:
                    route_pois[item]['validity'] = 1 #1 if point is now valid
            else:
                if (float_current_time > float(route_pois[item]['end_time'])) or (float_current_time > float(finish_time)):
                    route_pois[item]['validity'] = 0 #0 if point is now invalid
                else:
                    route_pois[item]['validity'] = 1 #1 if point is now valid
    return json.dumps(route_pois) 