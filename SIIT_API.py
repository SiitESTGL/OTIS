import requests

def request(url):
    r=requests.get(url)
    try:
        r_json = r.json()
    except ValueError:
        return ("Error code:" + str(r.status_code))
    return (r_json)

class API_client(object):
    
    def __init__(self, key=None,
                 address= app.config['DEFAULT_SERVER_HOST_ADDRESS']+"/api/v1.0/"
        self.key = key
        self.address = address


    def distance_coord(self, lat = None, lon = None, cat = None, conc = None, dist = None, num_poi=None, order=None):
        if lat is None or lon is None:
            return ("Error, missing Latitude or Longitude")
        if dist is None:
            return ("Error, missing distance")
        if not isinstance(lat, str):
            lat = str(lat)
        if not isinstance(lon, str):
            lon = str(lon)
        if cat is not None:
            if not isinstance(cat, str):
                cat = str(cat)
        if conc is not None:        
            if not isinstance(conc, str):
                conc = str(conc)
        if not isinstance(dist, str):
            dist = str(dist)
        if num_poi is not None:     
            if not isinstance(num_poi, str):
                num_poi = str(num_poi)
        if order is not None:     
            if not isinstance(order, str):
                order = str(order)
        if cat and conc and num_poi and order:
            url = self.address + "dist?lat="+lat+"&lon="+lon+"&numpoi="+num_poi+"&order="+order+"&cat="+cat+"&conc="+conc+"&dist="+dist+"&key="+self.key
        elif cat and num_poi and order:
            url = self.address + "dist?lat="+lat+"&lon="+lon+"&numpoi="+num_poi+"&order="+order+"&cat="+cat+"&dist="+dist+"&key="+self.key
        elif cat and num_poi:
            url = self.address + "dist?lat="+lat+"&lon="+lon+"&numpoi="+num_poi+"&cat="+cat+"&dist="+dist+"&key="+self.key
        elif cat and order:
            url = self.address + "dist?lat="+lat+"&lon="+lon+"&order="+order+"&cat="+cat+"&dist="+dist+"&key="+self.key   
        elif cat and conc:
            url = self.address + "dist?lat="+lat+"&lon="+lon+"&cat="+cat+"&conc="+conc+"&dist="+dist+"&key="+self.key
        elif cat:
            url = self.address + "dist?lat="+lat+"&lon="+lon+"&cat="+cat+"&dist="+dist+"&key="+self.key
        elif conc and num_poi and order:
            url = self.address + "dist?lat="+lat+"&lon="+lon+"&numpoi="+num_poi+"&order="+order+"&conc="+conc+"&dist="+dist+"&key="+self.key
        elif conc and num_poi:
            url = self.address + "dist?lat="+lat+"&lon="+lon+"&numpoi="+num_poi+"&conc="+conc+"&dist="+dist+"&key="+self.key      
        elif conc and order:
            url = self.address + "dist?lat="+lat+"&lon="+lon+"&order="+order+"&conc="+conc+"&dist="+dist+"&key="+self.key
        elif conc:
            url = self.address + "dist?lat="+lat+"&lon="+lon+"&conc="+conc+"&dist="+dist+"&key="+self.key
        elif num_poi and order:
            url = self.address + "dist?lat="+lat+"&lon="+lon+"&numpoi="+num_poi+"&order="+order+"&dist="+dist+"&key="+self.key
        elif num_poi:
            url = self.address + "dist?lat="+lat+"&lon="+lon+"&numpoi="+num_poi+"&dist="+dist+"&key="+self.key
        elif order:    
            url = self.address + "dist?lat="+lat+"&lon="+lon+"&order="+order+"&dist="+dist+"&key="+self.key
        else:
            url = self.address + "dist?lat="+lat+"&lon="+lon+"&dist="+dist+"&key="+self.key
        return request(url)
    
    def distance_id(self, poi_id = None, cat = None, conc = None, dist = None, num_poi=None, order=None):
        if poi_id is None:
            return ("Error, missing ID")
        if dist is None:
            return ("Error, missing distance")
        if not isinstance(poi_id, str):
            poi_id = str(poi_id)
        if cat is not None:
            if not isinstance(cat, str):
                cat = str(cat)
        if conc is not None:        
            if not isinstance(conc, str):
                conc = str(conc)
        if not isinstance(dist, str):
            dist = str(dist)
        if num_poi is not None:     
            if not isinstance(num_poi, str):
                num_poi = str(num_poi)
        if order is not None:     
            if not isinstance(order, str):
                order = str(order)
        if cat and conc and num_poi and order:
            url = self.address + "dist_id?id="+poi_id+"&numpoi="+num_poi+"&order="+order+"&cat="+cat+"&conc="+conc+"&dist="+dist+"&key="+self.key
        elif cat and num_poi and order:
            url = self.address + "dist_id?id="+poi_id+"&numpoi="+num_poi+"&order="+order+"&cat="+cat+"&dist="+dist+"&key="+self.key
        elif cat and num_poi:
            url = self.address + "dist_id?id="+poi_id+"&numpoi="+num_poi+"&cat="+cat+"&dist="+dist+"&key="+self.key
        elif cat and order:
            url = self.address + "dist_id?id="+poi_id+"&order="+order+"&cat="+cat+"&dist="+dist+"&key="+self.key   
        elif cat and conc:
            url = self.address + "dist_id?id="+poi_id+"&cat="+cat+"&conc="+conc+"&dist="+dist+"&key="+self.key
        elif cat:
            url = self.address + "dist_id?id="+poi_id+"&cat="+cat+"&dist="+dist+"&key="+self.key
        elif conc and num_poi and order:
            url = self.address + "dist_id?id="+poi_id+"&numpoi="+num_poi+"&order="+order+"&conc="+conc+"&dist="+dist+"&key="+self.key
        elif conc and num_poi:
            url = self.address + "dist_id?id="+poi_id+"&numpoi="+num_poi+"&conc="+conc+"&dist="+dist+"&key="+self.key      
        elif conc and order:
            url = self.address + "dist_id?id="+poi_id+"&order="+order+"&conc="+conc+"&dist="+dist+"&key="+self.key
        elif conc:
            url = self.address + "dist_id?id="+poi_id+"&conc="+conc+"&dist="+dist+"&key="+self.key
        elif num_poi and order:
            url = self.address + "dist_id?id="+poi_id+"&numpoi="+num_poi+"&order="+order+"&dist="+dist+"&key="+self.key
        elif num_poi:
            url = self.address + "dist_id?id="+poi_id+"&numpoi="+num_poi+"&dist="+dist+"&key="+self.key
        elif order:    
            url = self.address + "dist_id?id="+poi_id+"&order="+order+"&dist="+dist+"&key="+self.key
        else:
            url = self.address + "dist_id?id="+poi_id+"&dist="+dist+"&key="+self.key        
        return request(url)

    def time_coord(self, lat = None, lon = None, cat = None, conc = None, time = None, num_poi = None, order = None):
        if lat is None or lon is None:
            return ("Error, missing Latitude or Longitude")
        if time is None:
            return ("Error, missing time")
        if not isinstance(lat, str):
            lat = str(lat)
        if not isinstance(lon, str):
            lon = str(lon)
        if cat is not None:
            if not isinstance(cat, str):
                cat = str(cat)
        if conc is not None:        
            if not isinstance(conc, str):
                conc = str(conc)
        if not isinstance(time, str):
            time = str(time)
        if num_poi is not None:     
            if not isinstance(num_poi, str):
                num_poi = str(num_poi)
        if order is not None:     
            if not isinstance(order, str):
                order = str(order)
        if cat and conc and num_poi and order:
            url = self.address + "poi_time?lat="+lat+"&lon="+lon+"&numpoi="+num_poi+"&order="+order+"&cat="+cat+"&conc="+conc+"&time="+time+"&key="+self.key
        elif cat and num_poi and order:
            url = self.address + "poi_time?lat="+lat+"&lon="+lon+"&numpoi="+num_poi+"&order="+order+"&cat="+cat+"&time="+time+"&key="+self.key
        elif cat and num_poi:
            url = self.address + "poi_time?lat="+lat+"&lon="+lon+"&numpoi="+num_poi+"&cat="+cat+"&time="+time+"&key="+self.key
        elif cat and order:
            url = self.address + "poi_time?lat="+lat+"&lon="+lon+"&order="+order+"&cat="+cat+"&time="+time+"&key="+self.key   
        elif cat and conc:
            url = self.address + "poi_time?lat="+lat+"&lon="+lon+"&cat="+cat+"&conc="+conc+"&time="+time+"&key="+self.key
        elif cat:
            url = self.address + "poi_time?lat="+lat+"&lon="+lon+"&cat="+cat+"&time="+time+"&key="+self.key
        elif conc and num_poi and order:
            url = self.address + "poi_time?lat="+lat+"&lon="+lon+"&numpoi="+num_poi+"&order="+order+"&conc="+conc+"&time="+time+"&key="+self.key
        elif conc and num_poi:
            url = self.address + "poi_time?lat="+lat+"&lon="+lon+"&numpoi="+num_poi+"&conc="+conc+"&time="+time+"&key="+self.key      
        elif conc and order:
            url = self.address + "poi_time?lat="+lat+"&lon="+lon+"&order="+order+"&conc="+conc+"&time="+time+"&key="+self.key
        elif conc:
            url = self.address + "poi_time?lat="+lat+"&lon="+lon+"&conc="+conc+"&time="+time+"&key="+self.key
        elif num_poi and order:
            url = self.address + "poi_time?lat="+lat+"&lon="+lon+"&numpoi="+num_poi+"&order="+order+"&time="+time+"&key="+self.key
        elif num_poi:
            url = self.address + "poi_time?lat="+lat+"&lon="+lon+"&numpoi="+num_poi+"&time="+time+"&key="+self.key
        elif order:    
            url = self.address + "poi_time?lat="+lat+"&lon="+lon+"&order="+order+"&time="+time+"&key="+self.key
        else:
            url = self.address + "poi_time?lat="+lat+"&lon="+lon+"&time="+time+"&key="+self.key
        return request(url)
    
    def time_id(self, poi_id = None, cat = None, conc = None, time = None, num_poi=None, order=None):
        if poi_id is None:
            return ("Error, missing ID")
        if time is None:
            return ("Error, missing time")
        if not isinstance(poi_id, str):
            poi_id = str(poi_id)
        if cat is not None:
            if not isinstance(cat, str):
                cat = str(cat)
        if conc is not None:        
            if not isinstance(conc, str):
                conc = str(conc)
        if not isinstance(time, str):
            time = str(time)
        if num_poi is not None:     
            if not isinstance(num_poi, str):
                num_poi = str(num_poi)
        if order is not None:     
            if not isinstance(order, str):
                order = str(order)      
        if cat and conc and num_poi and order:
            url = self.address + "poi_time_id?id="+poi_id+"&numpoi="+num_poi+"&order="+order+"&cat="+cat+"&conc="+conc+"&time="+time+"&key="+self.key
        elif cat and num_poi and order:
            url = self.address + "poi_time_id?id="+poi_id+"&numpoi="+num_poi+"&order="+order+"&cat="+cat+"&time="+time+"&key="+self.key
        elif cat and num_poi:
            url = self.address + "poi_time_id?id="+poi_id+"&numpoi="+num_poi+"&cat="+cat+"&time="+time+"&key="+self.key
        elif cat and order:
            url = self.address + "poi_time_id?id="+poi_id+"&order="+order+"&cat="+cat+"&time="+time+"&key="+self.key   
        elif cat and conc:
            url = self.address + "poi_time_id?id="+poi_id+"&cat="+cat+"&conc="+conc+"&time="+time+"&key="+self.key
        elif cat:
            url = self.address + "poi_time_id?id="+poi_id+"&cat="+cat+"&time="+time+"&key="+self.key
        elif conc and num_poi and order:
            url = self.address + "poi_time_id?id="+poi_id+"&numpoi="+num_poi+"&order="+order+"&conc="+conc+"&time="+time+"&key="+self.key
        elif conc and num_poi:
            url = self.address + "poi_time_id?id="+poi_id+"&numpoi="+num_poi+"&conc="+conc+"&time="+time+"&key="+self.key      
        elif conc and order:
            url = self.address + "poi_time_id?id="+poi_id+"&order="+order+"&conc="+conc+"&time="+time+"&key="+self.key
        elif conc:
            url = self.address + "poi_time_id?id="+poi_id+"&conc="+conc+"&time="+time+"&key="+self.key
        elif num_poi and order:
            url = self.address + "poi_time_id?id="+poi_id+"&numpoi="+num_poi+"&order="+order+"&time="+time+"&key="+self.key
        elif num_poi:
            url = self.address + "poi_time_id?id="+poi_id+"&numpoi="+num_poi+"&time="+time+"&key="+self.key
        elif order:    
            url = self.address + "poi_time_id?id="+poi_id+"&order="+order+"&time="+time+"&key="+self.key
        else:
            url = self.address + "poi_time_id?id="+poi_id+"&time="+time+"&key="+self.key
        return request(url)       
    

    def route_calc(self, poi_id = None, cat = None, conc = None, days = None, duration = None, start_time = None):
        if poi_id is None:
            return ("Error, missing ID")
        if duration is None:
            return ("Error, missing duration")
        if start_time is None:
            return ("Error, missing start_time")
        if days is None:
            return ("Error, missing days")
        if not isinstance(poi_id, str):
            poi_id = str(poi_id)
        if cat is not None:
            if not isinstance(cat, str):
                cat = str(cat)
        if conc is not None:        
            if not isinstance(conc, str):
                conc = str(conc)
        if not isinstance(days, str):
            days = str(days)
        if not isinstance(duration, str):
            duration = str(duration)
        if not isinstance(start_time, str):
            start_time = str(start_time)
        if cat and conc:
            url = self.address + "route_calc_id?id="+poi_id+"&cat="+cat+"&conc="+conc+"&days="+days+"&start_time="+start_time+"&duration="+duration+"&key="+self.key
        elif cat:
            url = self.address + "route_calc_id?id="+poi_id+"&cat="+cat+"&days="+days+"&start_time="+start_time+"&duration="+duration+"&key="+self.key
        elif conc:
            url = self.address + "route_calc_id?id="+poi_id+"&conc="+conc+"&days="+days+"&start_time="+start_time+"&duration="+duration+"&key="+self.key
        else:
            url = self.address + "route_calc_id?id="+poi_id+"&days="+days+"&start_time="+start_time+"&duration="+duration+"&key="+self.key
        return request(url)

    def route_calc_coord(self, lat = None, lon = None, cat = None, conc = None, days = None, duration = None, start_time = None):
        if lat is None or lat is None:
            return ("Error, missing coordinates")
        if duration is None:
            return ("Error, missing duration")
        if start_time is None:
            return ("Error, missing start_time")
        if days is None:
            return ("Error, missing days")
        if not isinstance(lat, str):
            lat = str(lat)
        if not isinstance(lon, str):
            lon = str(lon)        
        if cat is not None:
            if not isinstance(cat, str):
                cat = str(cat)
        if conc is not None:        
            if not isinstance(conc, str):
                conc = str(conc)
        if not isinstance(days, str):
            days = str(days)
        if not isinstance(duration, str):
            duration = str(duration)
        if not isinstance(start_time, str):
            start_time = str(start_time)
        if cat and conc:
            url = self.address + "route_calc_coord?lat="+lat+"&lon="+lon+"&cat="+cat+"&conc="+conc+"&days="+days+"&start_time="+start_time+"&duration="+duration+"&key="+self.key
        elif cat:
            url = self.address + "route_calc_coord?lat="+lat+"&lon="+lon+"&cat="+cat+"&days="+days+"&start_time="+start_time+"&duration="+duration+"&key="+self.key
        elif conc:
            url = self.address + "route_calc_coord?lat="+lat+"&lon="+lon+"&conc="+conc+"&days="+days+"&start_time="+start_time+"&duration="+duration+"&key="+self.key
        else:
            url = self.address + "route_calc_coord?lat="+lat+"&lon="+lon+"&days="+days+"&start_time="+start_time+"&duration="+duration+"&key="+self.key
        return request(url)
    
    
    def poi_cat_conc(self, cat = None, conc = None, num_poi=None, min_score=None):
        if cat is None and conc is None:
            return ("Error, missing category or concelho")
        if cat is not None:
            if not isinstance(cat, str):
                cat = str(cat)
        if conc is not None:        
            if not isinstance(conc, str):
                conc = str(conc)
        if num_poi is not None:     
            if not isinstance(num_poi, str):
                num_poi = str(num_poi)
        if min_score is not None:     
            if not isinstance(min_score, str):
                min_score = str(min_score)      
        if cat and conc and num_poi and min_score:
            url = self.address + "poi?cat="+cat+"&conc="+conc+"&numpoi="+num_poi+"&score="+min_score+"&key="+self.key
        elif cat and num_poi and min_score:
            url = self.address + "poi?&numpoi="+num_poi+"&score="+min_score+"&cat="+cat+"&key="+self.key
        elif cat and num_poi:
            url = self.address + "poi?&numpoi="+num_poi+"&cat="+cat+"&key="+self.key
        elif cat and min_score:
            url = self.address + "poi?&score="+min_score+"&cat="+cat+"&key="+self.key   
        elif cat and conc:
            url = self.address + "poi?&cat="+cat+"&conc="+conc+"&key="+self.key
        elif cat:
            url = self.address + "poi&cat="+cat+"&key="+self.key
        elif conc and num_poi and min_score:
            url = self.address + "poi?&numpoi="+num_poi+"&score="+min_score+"&conc="+conc+"&key="+self.key
        elif conc and num_poi:
            url = self.address + "poi?&numpoi="+num_poi+"&conc="+conc+"&key="+self.key      
        elif conc and min_score:
            url = self.address + "poi?&score="+min_score+"&conc="+conc+"&key="+self.key
        elif conc:
            url = self.address + "poi?&conc="+conc+"&key="+self.key
        elif num_poi and min_score:
            url = self.address + "poi?&numpoi="+num_poi+"&score="+min_score+"&key="+self.key
        elif num_poi:
            url = self.address + "poi?&numpoi="+num_poi+"&key="+self.key
        elif min_score:    
            url = self.address + "poi?&score="+min_score+"&key="+self.key
        return request(url)  
    
    def poi_by_id(self, poi_id = None):
        if poi_id is None:
            return ("Error, missing ID")
        if not isinstance(poi_id, str):
            poi_id = str(poi_id)
        url = self.address + "poi_id?id="+poi_id+"&key="+self.key
        return request(url)
    
    def OSRM_poi_to_poi(self, poi_id = None, poi_id2 = None, profile = "driving"):
        if poi_id is None or poi_id2 is None:
            return ("Error, missing ID")
        profile = profile.lower()
        if not isinstance(poi_id, str):
            poi_id = str(poi_id)
        if not isinstance(poi_id2, str):
            poi_id2 = str(poi_id2)
        url = self.address + "osrm_poipoi?id="+poi_id+"&id2="+poi_id2+"&profile="+profile+"&key="+self.key
        return request(url)
    
    def OSRM_poi_to_coord(self, poi_id = None, lat = None, lon = None, profile = "driving", switch = 0):
        if poi_id is None:
            return ("Error, missing ID")
        if lat is None or lat is None:
            return ("Error, missing coordinates")
        profile = profile.lower()
        if not isinstance(poi_id, str):
            poi_id = str(poi_id)
        if not isinstance(lat, str):
            lat = str(lat)
        if not isinstance(lon, str):
            lon = str(lon)
        if switch == 1:
            url = self.address + "osrm_poipoint?id="+poi_id+"&lat="+lat+"&lon="+lon+"&profile="+profile+"&key="+self.key
        else:
            url = self.address + "osrm_pointpoi?id="+poi_id+"&lat="+lat+"&lon="+lon+"&profile="+profile+"&key="+self.key
        return request(url)
    
    def route_by_id(self, route_id = None):
        if route_id is None:
            return ("Error, missing ID")
        if not isinstance(route_id, str):
            route_id = str(route_id)
        url = self.address + "route_id?id="+route_id+"&key="+self.key
        return request(url)