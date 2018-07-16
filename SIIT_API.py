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

    def distance_coord(self, lat = None, lon = None, cat = None, conc = None, dist = None):
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
        if cat and conc:
            url = self.address + "dist?lat="+lat+"&lon="+lon+"&cat="+cat+"&conc="+conc+"&dist="+dist+"&key="+self.key
        elif cat:
            url = self.address + "dist?lat="+lat+"&lon="+lon+"&cat="+cat+"&dist="+dist+"&key="+self.key
        elif conc:
            url = self.address + "dist?lat="+lat+"&lon="+lon+"&conc="+conc+"&dist="+dist+"&key="+self.key
        else:
            url = self.address + "dist?lat="+lat+"&lon="+lon+"&dist="+dist+"&key="+self.key
        return request(url)
    
    def distance_id(self, poi_id = None, cat = None, conc = None, dist = None):
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
        if cat and conc:
            url = self.address + "dist_id?id="+poi_id+"&cat="+cat+"&conc="+conc+"&dist="+dist+"&key="+self.key
        elif cat:
            url = self.address + "dist_id?id="+poi_id+"&cat="+cat+"&dist="+dist+"&key="+self.key
        elif conc:
            url = self.address + "dist_id?id="+poi_id+"&conc="+conc+"&dist="+dist+"&key="+self.key
        else:
            url = self.address + "dist_id?id="+poi_id+"&dist="+dist+"&key="+self.key
        return request(url)

    def time_coord(self, lat = None, lon = None, cat = None, conc = None, time = None):
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
        if cat and conc:
            url = self.address + "poi_time?lat="+lat+"&lon="+lon+"&cat="+cat+"&conc="+conc+"&time="+time+"&key="+self.key
        elif cat:
            url = self.address + "poi_time?lat="+lat+"&lon="+lon+"&cat="+cat+"&time="+time+"&key="+self.key
        elif conc:
            url = self.address + "poi_time?lat="+lat+"&lon="+lon+"&conc="+conc+"&time="+time+"&key="+self.key
        else:
            url = self.address + "poi_time?lat="+lat+"&lon="+lon+"&time="+time+"&key="+self.key
        return request(url)
    
    def time_id(self, poi_id = None, cat = None, conc = None, time = None):
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
        if cat and conc:
            url = self.address + "poi_time_id?id="+poi_id+"&cat="+cat+"&conc="+conc+"&time="+time+"&key="+self.key
        elif cat:
            url = self.address + "poi_time_id?id="+poi_id+"&cat="+cat+"&time="+time+"&key="+self.key
        elif conc:
            url = self.address + "poi_time_id?id="+poi_id+"&conc="+conc+"&time="+time+"&key="+self.key
        else:
            url = self.address + "poi_time_id?id="+poi_id+"&time="+time+"&key="+self.key
        return request(url)

    def route_calc(self, poi_id = None, cat = None, conc = None, days = None, time = None):
        if poi_id is None:
            return ("Error, missing ID")
        if time is None:
            return ("Error, missing time")
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
        if not isinstance(time, str):
            time = str(time)
        if cat and conc:
            url = self.address + "route_calc_id?id="+poi_id+"&cat="+cat+"&conc="+conc+"&dias="+days+"&tempo="+time+"&key="+self.key
        elif cat:
            url = self.address + "route_calc_id?id="+poi_id+"&cat="+cat+"&dias="+days+"&tempo="+time+"&key="+self.key
        elif conc:
            url = self.address + "route_calc_id?id="+poi_id+"&conc="+conc+"&dias="+days+"&tempo="+time+"&key="+self.key
        else:
            url = self.address + "route_calc_id?id="+poi_id+"&dias="+days+"&tempo="+time+"&key="+self.key
        return request(url)
    
    def poi_cat_conc(self, cat = None, conc = None):
        if cat is None and conc is None:
            return ("Error, missing category or concelho")
        if cat is not None:
            if not isinstance(cat, str):
                cat = str(cat)
        if conc is not None:        
            if not isinstance(conc, str):
                conc = str(conc)
        if cat and conc:
            url = self.address + "poi?cat="+cat+"&conc="+conc+"&key="+self.key
        elif cat:
            url = self.address + "poi?cat="+cat+"&key="+self.key
        elif conc:
            url = self.address + "poi?conc="+conc+"&key="+self.key
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