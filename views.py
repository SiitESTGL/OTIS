# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, url_for, json, jsonify, session, make_response, abort, send_from_directory
from flask import redirect, flash, g

from flask_login import login_user, logout_user, current_user, login_required
from datetime import datetime, time

from app_core import app, db, login_manager
from models import User, Images
from My_functions import read_POIS_info, duration_check, route_poi_duration, route_poi_duration2, read_POIS_info2, read_route_info, decimal_second_to_hms, decimal_second_to_hms2
from my_function_osrm import get_trip_distance_duration


# --------------------------------------------------------------------
#
#
# --------------------------------------------------------------------
import flask_admin as admin
from app_admin import*
#  Admin View ----------------------------------------------------------------------------------
admin = admin.Admin(app, 'DouroRR APP', index_view=MyAdminIndexView(), base_template='admin/master_page.html',
                    template_mode='bootstrap3')

admin.add_view(PoisAdminView(name='POIs', endpoint="pois"))
admin.add_view(DistanceView(name='Distance', endpoint="distances"))
admin.add_view(SheduleView(name='Schedule', endpoint="schedule"))
admin.add_view(ImageAdminView(name='Images', endpoint="images"))
admin.add_view(UserView(name="Users", endpoint="user"))
admin.add_view(RouteView(name="Routes", endpoint="route"))
admin.add_view(CategoryView(name="Categories", endpoint="category"))
admin.add_view(ConcelhoView(name="Concelhos", endpoint="concelho"))
admin.add_view(LogView(name="Logs", endpoint="logs"))


# --------------------------------------------------------------------

# --------------------------------------------------------------------
# API View
# --------------------------------------------------------------------
from app_api import *

# --------------------------------------------------------------------

@app.context_processor
def inject_now():
    return {'now': datetime.datetime.utcnow()}

@app.route('/', methods=['POST', 'GET'])
def main():
    return home()


@app.route('/home', methods=['GET'])
def home():
    q = db.session.query(Images).filter(Images.img_check == 0)
    return render_template('home.html', img=q)


@app.route('/map', methods=['GET'])
def show_map():
    if request.method == 'GET':
        categ_id = "all"
        if request.args.get('category'):
            categ_id = request.args.get('category')
        category = Category.query.all()
        concelho = Concelho.query.all()
        poi_info2 = read_POIS_info2(categ_id)
        return render_template('map.html', poi_info=poi_info2, category=category, concelho=concelho)
    

@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')

@app.route('/api', methods=['GET'])
def api():
    category = Category.query.all()
    concelho = Concelho.query.all()
    return render_template('api.html', category = category, concelho = concelho)

@app.route('/api/tou', methods=['GET'])
def api_tou():
    return render_template('ToU.html')

@app.route('/routes', methods=['GET'])
def routes():
    route_info = read_route_info()
    return render_template('routes.html', route_info=route_info, drive = app.config['JS_OSRM_DRIVE_ADDRESS'], walk = app.config['JS_OSRM_WALK_ADDRESS'])


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    username = request.form['user_name']
    password = request.form['user_password']
    registered_user = User.authenticate(func.lower(username), password)
    if registered_user is False:
        flash('Username or Password is invalid', 'error')
        return redirect(url_for('login'))

    elif registered_user.is_admin or registered_user.is_super_admin:
        login_user(registered_user)
        return redirect(url_for('admin.index'))

    else:
        login_user(registered_user)
        return redirect(url_for('home'))  # request.args.get('next') or

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# --------------------------------------------------------------------
# Function called through AJAX in planner.js returns the points within the user's requested time frame
@app.route('/poidistance', methods=["GET", "POST"])
def poidistance():
    if request.method == "POST":
        poi_id= request.form['id']
        duration = request.form['duration']
        curr_pois = request.form['curr_pois']
        curr_pois2 = json.loads(curr_pois)
        return_time = request.form['return_time']
        curr_time = request.form['curr_time']
        wtl = request.form['wtl']
        checkfunc = duration_check(poi_id, duration, curr_pois2, return_time, curr_time, wtl)

        return checkfunc

@app.route('/route_duration', methods=["GET", "POST"])
def route_duration():
    if request.method == "POST":
        route_list = json.loads(request.form['route_pois'])
        duration = route_poi_duration(route_list)
        return duration
    
@app.route('/route_duration2', methods=["GET", "POST"])
def route_duration2():
    if request.method == "POST":
        route_list = json.loads(request.form['route_pois'])
        current_time = request.form['current_time']
        finish_time = request.form['finish_time']
        duration = route_poi_duration2(route_list, current_time, finish_time)
        return duration
    
    

# --------------------------------------------------------------------
# Function called through AJAX in routes.js returns the points within the user's requested route
@app.route('/route_point_get', methods=["GET", "POST"])
def route_point_get():
    if request.method == "POST":
        route_id = json.loads(request.form['route_id'])
        r = Route.query.get_or_404(route_id)
        info = []
        start_poi = []
        descript_pt = []
        descript_en = []
        position = []
        end_poi = []
        q = db.session.query(SequencePois).filter(SequencePois.route_id == r.id).all()

        for i in q:
            j = db.session.query(POIS).filter(POIS.id == i.pois_list).first()
            if j:
                poi_open_h2 = []
                poi_close_h2 = []
                poi_dura = []
                poi_phone = []
                poi_email = []
                poi_website = []
                poi_orig_img = []
                poi_copy_img = []
                sequence_image = []

                for item2 in j.poi_schedule:
                    poi_open_h_sec = item2.poi_open_h
                    poi_open_h = decimal_second_to_hms(float(item2.poi_open_h))
                    poi_close_h_sec = item2.poi_close_h
                    poi_close_h = decimal_second_to_hms(item2.poi_close_h)
                    POI_dura_sec = item2.poi_vdura
                    poi_vdura = decimal_second_to_hms2(item2.poi_vdura)
                    poi_open_h2.append(poi_open_h)
                    poi_close_h2.append(poi_close_h)
                    if len (poi_dura)<1:
                        poi_dura.append(poi_vdura)

                for item2 in j.poi_contact:
                    poi_phone.append(item2.telephone)
                    poi_email.append(item2.email)
                    poi_website.append(item2.website)

                for item2 in j.poi_image:
                    poi_orig_img.append(item2.original_img)
                    poi_copy_img.append(item2.copy_img)
                
                for item2 in i.sequence_image:
                    sequence_image.append(item2.original_img)
        
                info.append({
                    "pois": {
                        "routeID": i.route_id,
                        "travel_mode": r.mode_travel,
                        "poiID": j.id,
                        "poiName": j.poi_name,
                        "poiLat": j.poi_lat,
                        "poiLon": j.poi_lon,
                        "poiScore": j.poi_score,
                        "circle": r.route_isCircle,
                        "poi_descript_pt": j.poi_descri_pt_short,
                        "address": j.poi_address,
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
                        "route_descript_pt": i.descrip_start_end_pois_pt,
                        "sequence_review": i.sequence_review,
                        "sequence_image": sequence_image
                    }
                })
        if r.route_isCircle:
            info.append(info[0])

        for i, item in enumerate(r.sequence_pois):
            poi_start = POIS.query.get_or_404((item.start_poi_id))
            startpoiname = ""
            if poi_start:
                startpoiname = poi_start.poi_name
            start_poi.append({
                "start_poi": startpoiname
            })

            poi_end = POIS.query.get_or_404((item.end_poi_id))
            endpoiname = ""
            if poi_end:
                endpoiname = poi_end.poi_name
            end_poi.append({
                "end_poi": endpoiname
            })

            descript_pt.append({
                "descrip_pt": item.descrip_start_end_pois_pt
            })

            descript_en.append({
                "descript_en": item.descrip_start_end_pois_en
            })
            position.append({
                "index": i + 1
            })

        if not r.route_isCircle:  # if route is not circle, we to remove the default values, we have been added.
            start_poi.pop()
            end_poi.pop()
            descript_pt.pop()
            descript_en.pop()
            position.pop()

        info2 = list(zip(start_poi, descript_en, end_poi, position, descript_pt))
        return jsonify(info)


if __name__ == '__main__':
    app.run(port=8000, debug=True)
