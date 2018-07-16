# coding:utf-8

from math import *
from flask_login import login_required
import os
try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO
from PIL import Image
from flask import url_for, redirect, request, flash, json, jsonify, g, render_template, send_from_directory
from sqlalchemy import func
from sqlalchemy.event import listens_for
from werkzeug.utils import secure_filename
import flask_admin as admin
from threading import Thread
from celery.result import AsyncResult

from app_core import db, app, celery
from app_admin_function import *
from models import *
from my_function_osrm import *

ALLOWED_EXTENSIONS = (['png', 'jpg', 'jpeg'])

# function that checks if an uploaded image has the correct allowed extensions
def allowed_file(filename):
    return '.' in filename and \
           filename.lower().rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
    
                
class AdminAuthenctication_admin(object):  # Define class Admin Authentication_admin
    # define method is_accessible, to verify user, if user is authenticated and is he/she admin, return true
    def is_accessible(self):
        return g.user.is_authenticated and g.user.is_admin()


class AdminAuthenctication_superadmin(object):  # define class Admin Authentication super admin
    #  method  is_accessible to verify user, if user is authenticated and is he/she super admin return true.
    def is_accessible(self):
        return g.user.is_authenticated and g.user.is_super_admin()


# =====================================================================================================================+
# Create custom admin index view, by default Flask-Admin has empty index view.
# method index, shows dynamic images in the admin home page. This method executes, when click on radio buttons show and
# hide in the page list Images, to update state show and hide values from the database
# ---------------------------------------------------------------------------------------------------------------------+
class MyAdminIndexView(AdminAuthenctication_admin, AdminAuthenctication_superadmin, admin.AdminIndexView):
    
    @login_required  # Access this view, required login
    @admin.expose('/')  # define URL
    def index(self):

        show_state = db.session.query(Images).filter(Images.img_check == 0)
        self._template_args['img_show'] = show_state
        return super(MyAdminIndexView, self).index()


# =====================================================================================================================+
# The precedence code, Define Admin view for model POIS, and its methods CRUD (Create, read, update, delete)  and also
# method verifies data integrity such pois_name_unique()
# ---------------------------------------------------------------------------------------------------------------------+
class PoisAdminView(AdminAuthenctication_admin, AdminAuthenctication_superadmin, admin.BaseView):

    @login_required  # Access this view, required login
    @admin.expose('/')  # define URL
    def index(self):  # method index, default, return to method list poi.
        return redirect(url_for('.list_pois'))

    # This view selects pois information and returns the template with the information
    @login_required
    @admin.expose('/view')
    def list_pois(self):
        
        #creates list of dict keys that will be sent to the template
        column = ["id", "poi_name", "poi_lat", "poi_lon", "poi_categ", "last_update", "poi_review", "poi_en_review", "poi_future_review"]
        
        info_poi = []
        
        #queries all the POIS in the database and then checks for their category name and adds all the data to their respective keys
        #as defined above
        poi = POIS.query.all()
        for item in poi:
            category = Category.query.get(int(item.category_id))
            if category:
                categoryname = category.categ_name_pt
            else:
                categoryname = ""
            info_poi.append(dict(zip(column, [item.id, item.poi_name,
                                              item.poi_lat, item.poi_lon,
                                              categoryname,
                                              item.date_poi_updated,
                                              item.poi_review,
                                              item.poi_en_review,
                                              item.poi_future_review])))
        return self.render('admin/Pois_admin.html', poi=info_poi)

    # Create POIS --------------------------------------------------------
    @login_required
    @admin.expose('/create-pois', methods=['GET', 'POST'])
    def create_pois(self):
        """
         dms2decimal is  user's function  converts (degree, minute, second) to decimal number
        :return:
        """
        if request.method == 'POST':
            #starts by checking the forms relevant to data in the POIS table in the create HTML template and attributes it to variables
            p_lat = dms2decimal(int(request.form['lat_degree']), int(request.form['lat_minute']),
                                int(request.form['lat_second']), request.form['lat_direction'])
            p_lon = dms2decimal(int(request.form['long_degree']), int(request.form['long_minute']),
                                int(request.form['long_second']), request.form['long_direction'])

            myimage = request.files.getlist('imagefile[]')
            p_open = request.form.getlist('poi_open[]')
            p_duration = "0:0"
            if request.form['visitduration']:
                p_duration = request.form['visitduration']
            p_close = request.form.getlist('poi_close[]')

            pois = POIS(poi_name=request.form['poi_name'],
                        poi_lat=p_lat,
                        poi_lon=p_lon,
                        poi_descri_pt_short=request.form['poi_descri_pt_short'],
                        poi_descri_pt_long=request.form['poi_descri_pt_long'],
                        poi_descri_en_short=request.form['poi_descri_en_short'],
                        poi_descri_en_long=request.form['poi_descri_en_long'],
                        category_id=int(request.form['select_categ']),
                        concelho_id=int(request.form['select_conc']),
                        poi_score = int(request.form['select_score']),
                        poi_source=request.form['poi_source_info'],
                        poi_notes=request.form['poi_notes'],
                        poi_review = int(request.form['poistate_radio']),
                        poi_address = request.form['poi_address'],
                        poi_en_review = int(request.form['poistate_radio_en'])
                        )

            
            #processes the data for tables related to the POIS table, like contacts and schedules
            poi_contact = Contact(telephone=request.form['poi_phone'],
                                  email=request.form['poi_email'],
                                  website=request.form['poi_website'])
            
            pois.poi_contact.append(poi_contact)

            for index, item in enumerate(p_open):
                poi_schedule = POIS_schedule(
                    poi_open_h=convert_time_to_decimal(item),
                    is_open_or_close=int(request.form['typeradio_poi']),
                    poi_close_h=convert_time_to_decimal(p_close[index]),
                    poi_vdura=convert_time_to_decimal(p_duration))
                pois.poi_schedule.append(poi_schedule)

            imgview = ImageAdminView
            size = (843, 403)  # Resize image file
            for imgfile in myimage:
                if imgfile and allowed_file(imgfile.filename):
                    filename = secure_filename(imgfile.filename)
                    # path for a new image, after resize or crop
                    path_for_new_img = os.path.join(app.config['UPLOAD_FOLDER'], "copy_" + filename)

                    poi_img = Images(original_img=filename,
                                     img_descrip=pois.poi_name,
                                     copy_img="copy_" + filename,
                                     img_check=True
                                     )
                    pois.poi_image.append(poi_img)

                    imgfile.save(
                        os.path.join(app.config['UPLOAD_FOLDER'], filename))  # save original image file, uploads folder
                    imgview.image_cropper(os.path.join(app.config['UPLOAD_FOLDER'], filename)) # function to crop the images uploaded to the server

            db.session.add(pois)
            db.session.commit()
            flash('The POI %s has been created' % request.form['poi_name'], 'success')
            
            #after adding the POI, calculates the distance from this point to every other in the database using OSRM
            
            #-------
            #WARNING: If adding POIs becomes too slow, comment out this section and use the update distance button in the distances 
            #when you want to update the distances table
            #-------
            
            if pois.id:
                DistanceView.create_distance(pois.id)  # Calculate POI distance and duration
            return redirect(url_for('.detailview_pois', poi_id=pois.id))

        
        #Handle GET method
        poi_category = Category.query.with_entities(Category.categ_id, Category.categ_name_pt)
        poi_concelho = Concelho.query.with_entities(Concelho.conc_id, Concelho.conc_name)
        return self.render('admin/pois_create.html', poi_cat=poi_category, poi_conc=poi_concelho)
    
    #----------------------------------------------------------------------------------------------------------------+
    #Functions called through AJAX when pressing the checkboxes in order to change the different binary states of the POIs
    #----------------------------------------------------------------------------------------------------------------+
    @login_required
    @admin.expose('/change_poi_state', methods =['GET', 'POST'])
    def change_poi_state(self):
        if request.method == "POST":
            if "1" in request.form['check']:
                poi = POIS.query.get_or_404(int(request.form['poi_id']))
                if poi:
                    poi.poi_review = int(request.form['check'])
                    db.session.add(poi)
                    db.session.commit()
            else:
                poi = POIS.query.get_or_404(request.form['poi_id'])
                if poi:
                    poi.poi_review = int(request.form['check'])
                    db.session.add(poi)
                    db.session.commit()
                    
        return "NULL"
    
    
    @login_required
    @admin.expose('/change_poi_state2', methods =['GET', 'POST'])
    def change_poi_state2(self):
        if request.method == "POST":
            if "1" in request.form['check']:
                poi = POIS.query.get_or_404(int(request.form['poi_id']))
                if poi:
                    poi.poi_en_review = int(request.form['check'])
                    db.session.add(poi)
                    db.session.commit()
            else:
                poi = POIS.query.get_or_404(request.form['poi_id'])
                if poi:
                    poi.poi_en_review = int(request.form['check'])
                    db.session.add(poi)
                    db.session.commit()
                    
        return "NULL"
    
    @login_required
    @admin.expose('/change_poi_state3', methods =['GET', 'POST'])
    def change_poi_state3(self):
        if request.method == "POST":
            if "1" in request.form['check']:
                poi = POIS.query.get_or_404(int(request.form['poi_id']))
                if poi:
                    poi.poi_future_review = int(request.form['check'])
                    db.session.add(poi)
                    db.session.commit()
            else:
                poi = POIS.query.get_or_404(request.form['poi_id'])
                if poi:
                    poi.poi_future_review = int(request.form['check'])
                    db.session.add(poi)
                    db.session.commit()
                    
        return "NULL"
    
    # ----------------------------------------------------------------------------------------------------------------+
    # Check POI Name, if exist return msg True to javascript(Ajax)
    # ----------------------------------------------------------------------------------------------------------------+
    @login_required
    @admin.expose('/check-poiname', methods=['GET', 'POST'])
    def check_poi_name(self):
        state = "true"
        if request.method == 'POST':
            p_name = request.form['poi_name']
            if PoisAdminView.is_exist_poi_name(p_name):
                state = "false"
        return state
        # End checkpoi_name method ------------------------------------------------------------------------------------+

    @staticmethod
    def is_exist_poi_name(in_poi_name):
        """
        Verify point name in database, if exist then return true
        :param in_poi_name:
        :return: boolean
        """
        q = db.session.query(POIS.id).filter(func.lower(POIS.poi_name) == func.lower(in_poi_name))
        state = db.session.query(q.exists()).scalar()  # return true if exist
        return state
        # End method isExist_poi_name --------------------------------------------------------------------+

    
    # -----------------------------------------------------------------------------------------------------------------+
    # View to edit a specific POI, if request is POST recieve the data from the page and store it, else retrieve the data for the POI 
    # and return the edit page with the POI's data on it
    # -----------------------------------------------------------------------------------------------------------------+
    @login_required
    @admin.expose('/edit-pois/<poi_id>', methods=['GET', 'POST'])
    def edit_pois(self, poi_id):
        
        # queries the database to retrieve the data relevant to the point about to be edited
        poi_open_h = []
        poi_close_h = []
        poi_dura = []
        poi_img_id = []
        poi_img =[]

        categ = Category.query.all()
        conc = Concelho.query.all()
        p = POIS.query.get_or_404(poi_id)  # class Model POIS
        for item in p.poi_schedule:
            poi_open_h.append(item.poi_open_h)
            poi_close_h.append(item.poi_close_h)
            poi_dura.append(item.poi_vdura)
            
        for item2 in p.poi_image:
            poi_img_id.append(item2.img_id)
            poi_img.append(item2.original_img)

        duration_visit = db.session.query(POIS_schedule.poi_vdura).distinct().filter(
            POIS_schedule.poi_id == p.id).first()

        origimg = db.session.query(Images.copy_img).filter(Images.poi_id == p.id).all() 

        # Handle Post method
        if request.method == 'POST':
            p_lat = dms2decimal(int(request.form['lat_degree']), int(request.form['lat_minute']),
                                float(request.form['lat_second']), request.form['lat_direction'])

            p_lon = dms2decimal(int(request.form['long_degree']), int(request.form['long_minute']),
                                float(request.form['long_second']), request.form['long_direction'])

            file_path = request.files.getlist('imagefile[]')
            p_open = request.form.getlist('poi_open[]')
            p_close = request.form.getlist('poi_close[]')
            p_duration = convert_duration_to_standard_time(request.form.getlist('poi_duration[]'))
            sch_id_list = [index.id for index in POIS_schedule.query.with_entities(POIS_schedule.id).filter(POIS_schedule.poi_id == p.id)]
            p_duration = "0:0"
            if request.form['visitduration']:
                p_duration = request.form['visitduration']

            if p:  # is True or exist object
                
                #-------
                #WARNING: If editing POIs becomes too slow, comment out this section and use the update distance button in the distances 
                #when you want to update the distances table
                #-------
                
                
                if float(p.poi_lat) != float(p_lat) or float(p.poi_lon) != float(p_lon):
                    p.poi_lat = p_lat
                    p.poi_lon = p_lon
                    DistanceView.update_distance(poi_id, p_lat, p_lon) # computes  POI distances and duration            
                p.poi_name = request.form['poi_name']
                p.poi_lat = p_lat
                p.poi_lon = p_lon
                p.poi_descri_en_short = request.form['poi_descri_en_short']
                p.poi_descri_en_long=request.form['poi_descri_en_long']
                p.poi_descri_pt_short = request.form['poi_descri_pt_short']
                p.poi_descri_pt_long=request.form['poi_descri_pt_long']
                p.poi_score = int(request.form['select_score'])
                p.poi_notes = request.form['poi_notes']
                p.poi_source = request.form['poi_source_info']
                p.category_id = int(request.form['select_categ'])
                p.concelho_id = int(request.form['select_conc'])
                p.poi_review = int(request.form['poistate_radio'])
                p.poi_en_review = int(request.form['poistate_radio_en'])
                p.poi_future_review = int(request.form['poistate_radio_fut'])
                p.poi_address = request.form['poi_address']
                
                #if the length of the current form is identical to the original query it updates, else it deletes the current schedules and adds the data from the form
                if len(p_open)==len(sch_id_list):
                    for index, item in enumerate(p.poi_schedule):  # Update data in table Schedule
                        schedule = POIS_schedule.query.get_or_404(item.id)
                        if schedule:
                            schedule.poi_open_h = convert_time_to_decimal(p_open[index])
                            schedule.poi_close_h = convert_time_to_decimal(p_close[index])
                            schedule.poi_vdura = convert_time_to_decimal(p_duration)
                else:
                    schedelete = POIS_schedule.query.with_entities(POIS_schedule.id).filter(POIS_schedule.poi_id == p.id).delete()
                    for index, item in enumerate(p_open):
                        poi_schedule = POIS_schedule(
                            poi_open_h=convert_time_to_decimal(item),
                            poi_close_h=convert_time_to_decimal(p_close[index]),
                            poi_vdura=convert_time_to_decimal(p_duration))
                        p.poi_schedule.append(poi_schedule)
                    
                for item in p.poi_contact:  # Update data in table Contact
                    contact = Contact.query.get(item.contact_id)
                    contact.email = request.form['poi_email']
                    if contact.email == 'None':
                        contact.email = None
                    contact.telephone = request.form['poi_phone']
                    if contact.telephone == 'None':
                        contact.telephone = None
                    contact.website = request.form['poi_website']
                    if contact.website == 'None':
                        contact.website = None
                    
                imgview = ImageAdminView
                size = (843, 403)  # Resize image file
                for imgfile in file_path:
                    if imgfile and allowed_file(imgfile.filename):
                        filename = secure_filename(imgfile.filename)
                        # path for a new image, after resize or crop
                        path_for_new_img = os.path.join(app.config['UPLOAD_FOLDER'], "copy_" + filename)
                        imgfile2=imgfile
                        poi_img = Images(original_img=filename,
                                     img_descrip=p.poi_name,
                                     copy_img="copy_" + filename,
                                     img_check=True
                                     )
                        p.poi_image.append(poi_img)

                        imgfile.save(
                            os.path.join(app.config['UPLOAD_FOLDER'], filename))  # save original image file, uploads folder
                        imgview.image_cropper(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                db.session.commit()

                #queries the routes that contain the POI and updates its distance and duration
                routelist = list(db.session.query(SequencePois.route_id).distinct().filter(SequencePois.pois_list == p.id))
                for item, in routelist:
                    poi_list = []
                    start_pois = []
                    end_pois = []
                    r = Route.query.get_or_404(item)
                    for item in r.sequence_pois:
                        poi_list.append(item.pois_list)
                    if r.route_isCircle == 1:
                        poi_list.append(poi_list[0])
                    if r:
                        r.route_distan = get_route_distances(poi_list, r.mode_travel)
                        r.route_duration = get_route_duration(poi_list, r.mode_travel)
                    db.session.add(r)
            
            db.session.commit()
            flash('The POI %s has been Updated' % request.form['poi_name'], 'success')
            # DistanceView.update_distance(poi_id) # computes  POI distances and duration
            return redirect(url_for('.detailview_pois', poi_id=p.id))

        # Handle Got method
        else:
            default_open_close_hour = zip([poi_open_h[0]], [poi_close_h[0]], [poi_dura[0]])
            poi_open_h.pop(0)  # remove first item from poi_open_hour,  cause we save on default_open_hour
            poi_close_h.pop(0)  # remove also first item from poi_close_hour
            poi_dura.pop(0)
            open_close_hour = zip(poi_open_h, poi_close_h, poi_dura)
            print(open_close_hour)
            images = zip(poi_img_id, poi_img)
            
            return self.render('admin/pois_edit.html', poi=p, categ=categ, conc=conc,
                               default_open_close_hour=default_open_close_hour,
                               poi_open_close_h=open_close_hour, duration_visit=duration_visit, images=images)
        
    # -----------------------------------------------------------------------------------------------------------------+
    # Used to delete a specific point and all it's data
    # -----------------------------------------------------------------------------------------------------------------+
    @login_required
    @admin.expose('/delete-pois/<poi_id>')
    def delete_pois(self, poi_id):

        poi = POIS.query.get_or_404(poi_id)
        if poi:
            db.session.delete(poi)
        for item in poi.poi_image:
            try:
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], item.original_img))
            except OSError:
                pass
            try:
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], "256px_" + item.original_img))
            except OSError:
                pass
            try:
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], "512px_" + item.original_img))
            except OSError:
                pass
            try:
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], "1024px_" + item.original_img))
            except OSError:
                pass
            try:
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], "2048px_" + item.original_img))
            except OSError:
                pass
            try:
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], "4096px_" + item.original_img))
            except OSError:
                pass
            try:
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], item.copy_img))
            except OSError:
                pass

        db.session.commit()
        flash('The POI %s has been Deleted successfully' % poi.poi_name)
        DistanceView.delete_distance(poi_id)  # poi deleted success, delete also poi distances.
        return redirect(url_for('.list_pois'))
    
    # -----------------------------------------------------------------------------------------------------------------+
    # View for details about a POI
    # -----------------------------------------------------------------------------------------------------------------+
    @login_required
    @admin.expose('/detail-view/<poi_id>')
    def detailview_pois(self, poi_id):

        poi = POIS.query.get_or_404(poi_id)
        contact = db.session.query(Contact).filter(Contact.poi_id == poi.id).first()
        img = db.session.query(Images.original_img).filter(Images.poi_id == poi.id).first()        
        last_update = ""
        category = Category.query.get(poi.category_id)
        if category:
            categoryname = category.categ_name_pt
        else:
            categoryname = ""
        if poi.date_poi_updated:
            last_update = poi.date_poi_updated.strftime("%Y-%m-%d  %H:%M")
        return self.render('admin/pois_detailview.html', poi=poi, last_update=last_update,
                           categoryname=categoryname, contact=contact, img=img
                          )


# =====================================================================================================================+
# Define class ImageAdminView and it Implementation
# ---------------------------------------------------------------------------------------------------------------------+
class ImageAdminView(AdminAuthenctication_admin, AdminAuthenctication_superadmin, admin.BaseView):
    @login_required
    @admin.expose('/')  # default view
    def image_index(self):
        return redirect(url_for('.image'))

    @login_required
    @admin.expose('/view')
    def image(self):

        column = ["img_id", "img_descrip", "original_img", "copy_img", "img_check", "img_owner"]
        info_img = []
        img = Images.query.all()
        for item in img:
            if item.poi_id:
                poi = POIS.query.get(int(item.poi_id))
                if poi:
                    poiname = poi.poi_name
            else:
                poiname = ""
            info_img.append(dict(zip(column, [item.img_id, item.img_descrip,
                                              item.original_img, item.copy_img,
                                              item.img_check,
                                              poiname])))
        return self.render('admin/image.html', img=info_img)

    @login_required
    @admin.expose('/create-image', methods=['GET', 'POST'])
    def create_image(self):
        width, height = (1920, 1080)  # This default image size for our App, we can change this values.
        size = (width, height)
        filename = ""

        if request.method == 'POST':
            i_path = request.files['imageFile']
            if i_path and allowed_file(i_path.filename):
                filename = secure_filename(i_path.filename)

            # path for a new image, after resize or crop
            path_for_new_img = os.path.join(app.config['UPLOAD_FOLDER'], "copy_" + filename)

            image = Images(img_descrip=request.form['img_descrip'],
                           original_img=filename,
                           copy_img="copy_" + filename,
                           img_check=True)
            db.session.add(image)
            db.session.commit()

            i_path.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))  # save original image file, uploads folder
            # call method resize_crop_image
            ImageAdminView.image_cropper(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash('The Image %s was created successfully' % filename)
            return redirect(url_for('.image_index'))

        return self.render('admin/image_create.html')

    @login_required
    @admin.expose('/delete-image/<img_id>')
    def delete_image(self, img_id):

        img = Images.query.get_or_404(img_id)

        db.session.delete(img)
        db.session.commit()
        msg = img.original_img
        flash('The Image %s has been deleted successfully' % msg)
        return redirect(url_for('.image'))
    
    #----------------------------------------------------------------------------------------------------------------+   
    #Function that deletes an image in the POI edit page and returns to it after deletion
    #----------------------------------------------------------------------------------------------------------------+
    
    @login_required
    @admin.expose('/delete-image-edit/<img_id>')
    def delete_image_edit(self, img_id):

        img = Images.query.get_or_404(img_id)
        poi_id= img.poi_id
        
        db.session.delete(img)
        db.session.commit()
        msg = img.original_img
        flash('The Image %s has been deleted successfully' % msg)
        return redirect( url_for('pois.edit_pois', poi_id = poi_id))
    
    @login_required    
    @admin.expose('/delete-image-edit-route/<img_id>')
    def delete_image_edit_route(self, img_id):

        img = Images.query.get_or_404(img_id)
        route_id= img.route_id
        
        db.session.delete(img)
        db.session.commit()
        msg = img.original_img
        flash('The Image %s has been deleted successfully' % msg)
        return redirect( url_for('route.edit_route', route_id = route_id))

    @login_required
    @admin.expose('/edit-image/<img_id>', methods=["GET", "POST"])
    def edit_image(self, img_id):

        width, height = (843, 403)  # This default image size for our App, we can change this values.
        size = (width, height)
        filename = ""
        i = Images.query.get_or_404(img_id)
        print("hrellooo")

        if request.method == "POST":
            i_path = request.files["img_file"]
            print("somteing", request.files["img_file"])
            if i_path and allowed_file(i_path.filename):
                filename = secure_filename(i_path.filename)
                # path for a new image, after resize or crop
                path_for_new_img = os.path.join(app.config['UPLOAD_FOLDER'], "copy_" + filename)

                #  try to remove old images file from system
                try:
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], i.original_img))
                except OSError:
                    pass
                try:
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], i.copy_img))
                except OSError:
                    pass

            if i:
                i.img_descrip = request.form["img_descrip"]
                i.original_img = filename
                i.copy_img = "copy_" + filename
                db.session.commit()

                i_path.save(
                    os.path.join(app.config['UPLOAD_FOLDER'], filename))  # save original image file, uploads folder
                ImageAdminView.image_cropper(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                flash('The Image %s has been Updated successfully' % filename)
                return redirect(url_for('.image'))
        else:
            return self.render("admin/image_edit.html", image=i)
        
    #----------------------------------------------------------------------------------------------------------------+   
    #View for the page that allows for downloading the original image and upload a crop to display on the webpage
    #----------------------------------------------------------------------------------------------------------------+
    @login_required
    @admin.expose('/crop-image/<img_id>', methods=["GET", "POST"])
    def crop_image(self, img_id):

        width, height = (843, 403)  # This default image size for our App, we can change this values.
        size = (width, height)
        filename = ""
        i = Images.query.get_or_404(img_id)
        print("hrellooo")

        if request.method == "POST":
            i_path = request.files["img_file"]
            print("somteing", request.files["img_file"])
            if i_path and allowed_file(i_path.filename):
                filename = secure_filename(i_path.filename)
                # path for a new image, after resize or crop
                path_for_new_img = os.path.join(app.config['UPLOAD_FOLDER'], "copy_" + i.original_img)

                #  try to remove old image file from system
                try:
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], i.copy_img))
                except OSError:
                    pass

            if i:
                i.copy_img = "copy_" + i.original_img
                i.img_check=False
                db.session.commit()

                i_path.save(
                    os.path.join(path_for_new_img))  # save cropped image file, uploads folder
                
                flash('The Image %s has been Updated successfully' % i.original_img)
                return redirect(url_for('.image'))
        else:
            return self.render("admin/image_crop.html", image=i)
    
    @login_required
    @admin.expose('/get-imagesize', methods=['GET', 'POST'])
    def get_imagsize(self):
        io_stream_file = StringIO()
        if request.method == "GET":
            return self.render("admin/test_I.html")
        else:
            i_path = request.files['imageFile']
            i_path.save(io_stream_file)  # To stored in object StringIO
            width, height = (843, 403)
            size = (width, height)
            crop_type = 'bottom'
            filename = secure_filename(i_path.filename)
            my_path = (os.path.join(app.config['UPLOAD_FOLDER'], "copy " + filename))
        
    #----------------------------------------------------------------------------------------------------------------+   
    #Function that receives an image from a path and crops it into several levels of lower resolution based on its resolution
    #----------------------------------------------------------------------------------------------------------------+
    def image_cropper(filepath):
        image = Image.open(filepath)
        width = image.width
        height = image.height
        filename = secure_filename(image.filename)
        path = app.config['UPLOAD_FOLDER']
        path_replace = path.replace("/", "_")
        split_name = filename.replace(path_replace[0:], '')
        if width > 256 or height > 256:
            dest_path = os.path.join(app.config['UPLOAD_FOLDER'], "256px_" + split_name)
            size = (256,256)
            image.thumbnail(size, Image.ANTIALIAS)
            image.save(dest_path)
            image = Image.open(filepath)
        if width > 512 or height > 512:
            dest_path = os.path.join(app.config['UPLOAD_FOLDER'], "512px_" + split_name)
            size = (512,512)
            image.thumbnail(size, Image.ANTIALIAS)
            image.save(dest_path)
            image = Image.open(filepath)
        if width > 1024 or height > 1024:
            dest_path = os.path.join(app.config['UPLOAD_FOLDER'], "1024px_" + split_name)
            size = (1024,1024)
            image.thumbnail(size, Image.ANTIALIAS)
            image.save(dest_path)
            image = Image.open(filepath)
        if width > 2048 or height > 2048:
            dest_path = os.path.join(app.config['UPLOAD_FOLDER'], "2048px_" + split_name)
            size = (2048,2048)
            image.thumbnail(size, Image.ANTIALIAS)
            image.save(dest_path)
            image = Image.open(filepath)
        if width > 4096 or height > 4096:
            dest_path = os.path.join(app.config['UPLOAD_FOLDER'], "4096px_" + split_name)
            size = (4096,4096)
            image.thumbnail(size, Image.ANTIALIAS)
            image.save(dest_path)
            image = Image.open(filepath)
        return None


# ----------------------------------------------------------------------------------------+
# Deletes the resizes created by the above function on image delete
# ----------------------------------------------------------------------------------------+

@listens_for(Images, 'after_delete')
def delete_img_file(mapper, connection, target):
    if target.original_img:
        # Delete Image
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], target.original_img))
        except OSError:
            pass
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], "256px_" + target.original_img))
        except OSError:
            pass
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], "512px_" + target.original_img))
        except OSError:
            pass
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], "1024px_" + target.original_img))
        except OSError:
            pass
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], "2048px_" + target.original_img))
        except OSError:
            pass
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], "4096px_" + target.original_img))
        except OSError:
            pass
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], target.copy_img))
        except OSError:
            pass


# Dynamic Info ------------------------------------------------------------------------------------------------
class DistanceView(AdminAuthenctication_superadmin, AdminAuthenctication_admin, admin.BaseView):
    # Default view -------------------------------
    @login_required
    @admin.expose('/')
    def distan_index(self):
        return redirect(url_for('.poi_distance'))

    # query distance information---------------------------------------------------------------------------------------+
    @login_required
    @admin.expose('/view', methods=['GET', 'POST'])
    def poi_distance(self):
        start_poi = db.session.query(POIS, POIS_distances).filter(POIS.id == POIS_distances.start_poi_id).limit(3000).all()
        info_star = []
        columns = ["id", "Start_POI", "End_POI", "Distances", "Duration"]
        my_collection = []
        for i in start_poi:
            info_star.append(i.POIS.poi_name)
        
        db.session.flush
        end_poi = db.session.query(POIS_distances, POIS).filter(POIS_distances.end_poi_id == POIS.id).limit(3000).all()
        for i, elem in enumerate(end_poi):
            try:
                tmp_infostart = info_star[i]
            except IndexError:
                tmp_infostart = ""

            my_collection.append(dict(zip(columns,
                                          [elem.POIS_distances.id, tmp_infostart, elem.POIS.poi_name,
                                           elem.POIS_distances.trip_distance,
                                           elem.POIS_distances.trip_duration])))
    #When pressing the update button it submits a POST request, executing the following code --------------------------+
            if request.method == 'POST':
                columns2 = ["poi_id", "poi_lon", "poi_lat"]
                poi_dict = []
                pois = db.session.query(POIS)
                new_pois_id = [index.id for index in POIS.query.with_entities(POIS.id)]  # Assign all POIs ID to new list
                for i in pois:
                    poi_dict.append(dict(zip(columns2, [i.id, i.poi_lon, i.poi_lat]))) #Create dict with points and coords so Celery can calculate the distances without having the DB stay open throught the process
                update = DistanceView.poi_updateall_async.delay(*poi_dict)
                task_id=update.id
                return redirect(url_for('.update_distance_status', task_id=task_id))
        return self.render('admin/distance.html', my_colletion=my_collection)

    # View task status and progress---------------------------------------------------------------------------------------+

    @staticmethod
    def create_distance(poi_id):
        origin = POIS.query.get(poi_id)
        for index in POIS.query.with_entities(POIS.id):
            destin = POIS.query.get(index.id)
            #  Call Function get_trip_distance_duration,
            # it defined in file: my_function_osrm.py, return tuple, distance and duration
            distance, duration = get_trip_distance_duration([origin.poi_lon, origin.poi_lat],
                                                            [destin.poi_lon, destin.poi_lat])
            distance_walk, duration_walk = get_trip_distance_duration_walk([origin.poi_lon, origin.poi_lat],
                                                            [destin.poi_lon, destin.poi_lat])
            poi_distance = POIS_distances(
                start_poi_id=poi_id,
                end_poi_id=index.id,
                trip_duration=duration,  # duration,
                trip_distance=distance,  # distance
                trip_duration_walk=duration_walk, #duration on foot
                trip_distance_walk=distance_walk #distance on foot
            )
            db.session.add(poi_distance)
        db.session.commit()

    @staticmethod
    def delete_distance(poi_id):
        poidistan_info = db.session.query(POIS_distances).filter(POIS_distances.start_poi_id == poi_id).all()
        for item in poidistan_info:
            p_distance = POIS_distances.query.get(item.id)
            if p_distance:
                db.session.delete(p_distance)
        db.session.commit()

    @staticmethod
    def update_distance(poi_id, lat, lon):

        new_pois_id = [index.id for index in POIS.query.with_entities(POIS.id)]  # Assign all POIs ID to new list

        poi_info = db.session.query(POIS_distances).filter(POIS_distances.start_poi_id == poi_id).all()
        for i, keys in enumerate(poi_info):
            destin = POIS.query.get_or_404(keys.end_poi_id)
            distance, duration = get_trip_distance_duration([lon, lat],
                                                           [destin.poi_lon, destin.poi_lat])
            keys.trip_duration = duration
            keys.trip_distance = distance
        
        poi_info2 = db.session.query(POIS_distances).filter(POIS_distances.end_poi_id == poi_id).all()
        for i, keys in enumerate(poi_info2):
            origin = POIS.query.get_or_404(keys.start_poi_id)
            distance, duration = get_trip_distance_duration([origin.poi_lon, origin.poi_lat],
                                                           [lon, lat])
            keys.trip_duration = duration
            keys.trip_distance = distance
        db.session.commit()
    #View to check up on the progress of a specific task based on it's ID, used to see the progress on the distance update    
    @login_required
    @admin.expose('/update-status/<task_id>')
    def update_distance_status(self, task_id):
        re = DistanceView.poi_updateall_async.AsyncResult(task_id)
        res = re.result
        return self.render('admin/distance_status.html', res=res)
    
        
    # Define the asynchronous function Celery will use to update all the distances between each point
    # In case of changes to this function, please remember to restart the Celery service or the server itself in order to load the new version.
    @celery.task(bind=True)
    def poi_updateall_async(self, *pois):
        columns = ["Start_POI", "End_POI", "Duration", "Distance", "Duration_walk", "Distance_walk"]
        tripdict = []
        numpoi = len(pois)
        final_len = numpoi*numpoi
        for i in range (0,numpoi):
            for j in range (0,numpoi):
                #calculates the distance and durations on foot and by driving and adds them to the dictionary to be added to the DB
                distance, duration = get_trip_distance_duration([pois[i]['poi_lon'],pois[i]['poi_lat']],
                                                                [pois[j]['poi_lon'],pois[j]['poi_lat']])
                distance_walk, duration_walk = get_trip_distance_duration_walk([pois[i]['poi_lon'],pois[i]['poi_lat']],
                                                                [pois[j]['poi_lon'],pois[j]['poi_lat']])
                tripdict.append(dict(zip(columns, [pois[i]['poi_id'], pois[j]['poi_id'], duration, distance, duration_walk, distance_walk])))
                #updates the state of the task so the user can check up on its progress
                self.update_state(state='PROGRESS', meta={'current': len(tripdict), 'total': final_len, 'status': "Updating..."})
        lentrip = len(tripdict)
        delete = db.session.query(POIS_distances).delete()
        poi_info_count = db.session.query(POIS_distances)
        for l in range (0,lentrip):
            poi_distance = POIS_distances(
            start_poi_id=tripdict[l]['Start_POI'],
            end_poi_id=tripdict[l]['End_POI'],
            trip_duration=tripdict[l]['Duration'],  # duration,
            trip_distance=tripdict[l]['Distance'],  # distance,
            trip_duration_walk=tripdict[l]['Duration_walk'],  # duration on foot,
            trip_distance_walk=tripdict[l]['Distance_walk']  # distance on foot,
            )
            
            db.session.add(poi_distance)
        
        db.session.commit()
        return {'current': len(tripdict), 'total': final_len, 'status': 'Task completed!'}

class SheduleView(AdminAuthenctication_superadmin, AdminAuthenctication_admin, admin.BaseView):
    # Default index view
    @login_required
    @admin.expose('/')
    def schedule_index(self):
        return redirect(url_for('.list_schedule'))

    @login_required
    @admin.expose('/view')
    def list_schedule(self):
        poi_info = db.session.query(POIS, POIS_schedule.poi_id).filter(
            POIS.id == POIS_schedule.poi_id).all()

        schedule_info = []
        for item in poi_info:
            schedule = db.session.query(POIS_schedule).filter(POIS_schedule.poi_id == item.POIS.id)
            schedule_info.append({
                "poi_id": item.POIS.id,
                "poi_name": item.POIS.poi_name,
                "poi_duration": [i.poi_vdura for i in schedule],
                "poi_open_hour": [i.poi_open_h for i in schedule],
                "poi_close_h": [i.poi_close_h for i in schedule]
            })

        return self.render('admin/schedule.html', schedule_info=schedule_info)


# ---------------------------------------------------------------------------------------------------------------------+
# Implementation User Admin View
# ---------------------------------------------------------------------------------------------------------------------+
class UserView(AdminAuthenctication_superadmin, AdminAuthenctication_admin, admin.BaseView):
    # Default index view
    @login_required
    @admin.expose('/')
    def user_index(self):
        return redirect(url_for('.user_list'))

    @login_required
    @admin.expose('/view')
    def user_list(self):
        user = User.query.all()
        column = ["user_id", "username", "password", "email", "admin", "registered_on", "api_key"]
        info_user = []
        for item in user:
            key = db.session.query(API_Key.key).filter(API_Key.user_id == item.user_id).first()
            info_user.append(dict(zip(column, [item.user_id, item.username, item.password,
                                              item.email, item.admin,
                                              item.registered_on,
                                              key])))
        return self.render('admin/user.html', user=info_user)

    @login_required
    @admin.expose('/create-user', methods=["GET", "POST"])
    def create_user(self):
        if request.method == 'GET':
            return self.render('admin/user_create.html')
        admin = 0
        superadmin = 0
        value = int(request.form['typeradio_admin'])
        if value == 1:
            admin = 1
        elif value == 2:
            admin = 1
            superadmin = 1

        user = User.create(
            username=request.form['user_name'].lower(),
            password=request.form['user_password'],
            email=request.form['user_email'],
            admin=admin,
            superadmin=superadmin
        )
        if int(request.form['typeradio_api']) == 0:
            user_key = API_Key(key = generate_hash_key())
        
            user.user_key.append(user_key)

        db.session.add(user)
        db.session.commit()
        flash('User %s created successfully' % request.form['user_name'])
        return redirect(url_for('.user_list'))

    @login_required
    @admin.expose('/edit-user/<user_id>', methods=["GET", "POST"])
    def edit_user(self, user_id):
        user = User.query.get_or_404(user_id)
        if request.method == "GET":
            return self.render('admin/user_edit.html', user=user)
        admin = 0
        superadmin = 0
        value = int(request.form['typeradio'])
        print("value: ", value)
        if value == 1:
            admin = 1
        elif value == 2:
            admin = 1
            superadmin = 1

        if user:
            user.username = request.form['user_name'].lower()
            if int(request.form['typeradio_pass']) == 0:
                user.password = user.make_password(request.form['user_password'])
            user.email = request.form['user_email']
            user.admin = admin
            user.super_admin = superadmin
            
            if int(request.form['typeradio_api']) == 0 and len(user.user_key.all()) == 0:
                user_key = API_Key(key = generate_hash_key())
        
                user.user_key.append(user_key)
            
            elif int(request.form['typeradio_api']) == 1:
            
                user.user_key.delete()
            

            db.session.add(user)
            db.session.commit()
            flash("Your account has been updated successfully.")
            return redirect(url_for('.user_list'))

    @login_required
    @admin.expose('/delete-user/<user_id>')
    def user_delete(self, user_id):
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        flash('The user %s has been deleted successfully' % user.username)
        return redirect(url_for('.user_list'))

    @admin.expose('/check-unique-user', methods=['GET', 'POST'])
    def unique_user(self):
        state = "true"
        if request.method == 'POST':
            username = request.form['user_name']
            print (username)
            if UserView.exist_username(username):
                state = "false"
        return state

    @staticmethod
    def exist_username(input_username):
        u = db.session.query(User.user_id).filter(func.lower(User.username) == func.lower(input_username))
        result = db.session.query(u.exists()).scalar()  # return true if user name exist
        return result

    @admin.expose('/unique-email', methods=['GET', 'POST'])
    def unique_email(self):
        state = "true"
        if request.method == 'POST':
            email = request.form['user_email']
            print(email)
            if UserView.exist_email(email):
                state = "false"
        return state

    @staticmethod
    def exist_email(input_email):
        u_email = db.session.query(User.user_id).filter(func.lower(User.email) == func.lower(input_email))
        return db.session.query(u_email.exists()).scalar()  # return true, if email exist


# =====================================================================================================================#
# Create, edit, delete POI Category
class CategoryView(AdminAuthenctication_admin, AdminAuthenctication_superadmin, admin.BaseView):
    @login_required
    @admin.expose('/')
    def category_index(self):

        return redirect(url_for('.category_list'))

    @login_required
    @admin.expose('/category-list')
    def category_list(self):
        category = Category.query.all()
        return self.render('admin/category_list.html', categ=category)

    @login_required
    @admin.expose('/create-category', methods=['GET', 'POST'])
    def create_category(self):
        if request.method == 'GET':
            return self.render('admin/category_create.html')

        else:
            categ = Category(categ_name_pt=request.form['category_pt'],
                             categ_name_en=request.form['category_en'])
            db.session.add(categ)
            db.session.commit()
            flash("The category %s has been created successfully!" % request.form['category_en'])
            return redirect(url_for('.category_list'))

    @login_required
    @admin.expose('/edit-category<categ_id>', methods=['GET', 'POST'])
    def edit_category(self, categ_id):
        category = Category.query.get_or_404(categ_id)
        if request.method == 'GET':
            return self.render('admin/category_edit.html', category=category)

        if category:
            category.categ_name_pt = request.form['category_pt']
            category.categ_name_en = request.form['category_en']
        db.session.commit()
        flash("The category %s has been updated successfully!" % request.form['category_en'])
        return redirect(url_for('.category_list'))

    @login_required
    @admin.expose('/delete-category/<categ_id>')
    def delete_category(self, categ_id):
        category = Category.query.get_or_404(categ_id)
        if category:
            db.session.delete(category)
            db.session.commit()
        flash('The category %s has beeen deleted successfully' % category.categ_name_pt)
        return redirect(url_for('.category_list'))

    # Check POI category(pt) name must be unique
    @login_required
    @admin.expose('/check-unique-category-pt', methods=['GET', 'POST'])
    def unique_category_pt(self):
        state = "true"
        if request.method == 'POST':
            if CategoryView.is_exist_category_pt(request.form['category_pt']):
                state = "false"
        return state

    @staticmethod
    def is_exist_category_pt(input_categ):
        categ_pt = db.session.query(Category.categ_id).filter(
            func.lower(Category.categ_name_pt) == func.lower(input_categ))
        return db.session.query(categ_pt.exists()).scalar()  # return true, if poi category name existed

    # Check poi category(en) name must be unique
    @login_required
    @admin.expose('/check-unique-category-en', methods=['GET', 'POST'])
    def unique_category_en(self):
        state = "true"
        if request.method == 'POST':
            if CategoryView.is_exist_category_en(request.form['category_en']):
                state = "false"
        return state

    @staticmethod
    def is_exist_category_en(input_categ):
        categ_en = db.session.query(Category.categ_id).filter(
            func.lower(Category.categ_name_en) == func.lower(input_categ))
        return db.session.query(categ_en.exists()).scalar()  # return true, if poi category name existed
    
# =====================================================================================================================#
# Create, edit, delete POI Concelho
class ConcelhoView(AdminAuthenctication_admin, AdminAuthenctication_superadmin, admin.BaseView):
    @login_required
    @admin.expose('/')
    def concelho_index(self):

        return redirect(url_for('.concelho_list'))

    @login_required
    @admin.expose('/concelho-list')
    def concelho_list(self):
        concelho= Concelho.query.all()
        return self.render('admin/concelho_list.html', conc=concelho)

    @login_required
    @admin.expose('/create-concelho', methods=['GET', 'POST'])
    def create_concelho(self):
        if request.method == 'GET':
            return self.render('admin/concelho_create.html')

        else:
            concelho = Concelho(conc_name=request.form['concelho'])
            db.session.add(concelho)
            db.session.commit()
            flash("The concelho %s has been created successfully!" % request.form['concelho'])
            return redirect(url_for('.concelho_list'))

    @login_required
    @admin.expose('/edit-concelho<conc_id>', methods=['GET', 'POST'])
    def edit_concelho(self, conc_id):
        concelho = Concelho.query.get_or_404(conc_id)
        if request.method == 'GET':
            return self.render('admin/concelho_edit.html', concelho=concelho)

        if concelho:
            concelho.conc_name = request.form['concelho']
        db.session.commit()
        flash("The concelho %s has been updated successfully!" % request.form['concelho'])
        return redirect(url_for('.concelho_list'))

    @login_required
    @admin.expose('/delete-concelho/<conc_id>')
    def delete_concelho(self, conc_id):
        concelho = Concelho.query.get_or_404(conc_id)
        if concelho:
            db.session.delete(concelho)
            db.session.commit()
        flash('The county %s has beeen deleted successfully' % concelho.conc_name)
        return redirect(url_for('.concelho_list'))

    # Check POI concelho name must be unique
    @login_required
    @admin.expose('/check-unique-concelho', methods=['GET', 'POST'])
    def unique_concelho(self):
        state = "true"
        if request.method == 'POST':
            if ConcelhoView.is_exist_concelho(request.form['concelho']):
                state = "false"
        return state

    @staticmethod
    def is_exist_concelho(input_conc):
        conc = db.session.query(Concelho.conc_id).filter(
            func.lower(Concelho.conc_name) == func.lower(input_conc))
        return db.session.query(conc.exists()).scalar()  # return true, if poi category name existed

    
# =====================================================================================================================+
# Define  class RouteView  and implementation
# ---------------------------------------------------------------------------------------------------------------------+
class RouteView(AdminAuthenctication_admin, AdminAuthenctication_superadmin, admin.BaseView):
    @login_required
    @admin.expose('/')
    def index(self):

        return redirect(url_for('.route'))

    @login_required
    @admin.expose('/list')
    def route(self):
        route = Route.query.all()
        return self.render("admin/route_list.html", route=route)
    
# ---------------------------------------------------------------------------------------------------------------------+
# Function to change whether the route is valid or not using the checkboxes on the route list page
# ---------------------------------------------------------------------------------------------------------------------+
    @login_required
    @admin.expose('/change_route_state', methods =['GET', 'POST'])
    def change_route_state(self):
        if request.method == "POST":
            if "1" in request.form['check']:
                route = Route.query.get_or_404(int(request.form['route_id']))
                if route:
                    route.route_review = int(request.form['check'])
                    db.session.add(route)
                    db.session.commit()
            else:
                route = Route.query.get_or_404(request.form['route_id'])
                if route:
                    route.route_review = int(request.form['check'])
                    db.session.add(route)
                    db.session.commit()
                    
        return "NULL"
    
    @login_required
    @admin.expose('/change_route_state2', methods =['GET', 'POST'])
    def change_route_state2(self):
        if request.method == "POST":
            if "1" in request.form['check']:
                route = Route.query.get_or_404(int(request.form['route_id']))
                if route:
                    route.route_en_review = int(request.form['check'])
                    db.session.add(route)
                    db.session.commit()
            else:
                route = Route.query.get_or_404(request.form['route_id'])
                if route:
                    route.route_en_review = int(request.form['check'])
                    db.session.add(route)
                    db.session.commit()
                    
        return "NULL"

    @admin.expose('/display-routes<route_id>')
    def display_routes(self, route_id):

        r = Route.query.get_or_404(route_id)
        info = []
        start_poi = []
        descript_pt = []
        descript_en = []
        position = []
        end_poi = []
        q = db.session.query(SequencePois).filter(SequencePois.route_id == r.id).all()

        for i in q:
            poi = db.session.query(POIS).filter(POIS.id == i.pois_list).all()
            for j in poi:
                info.append({
                    "pois": {
                        "routeID": i.route_id,
                        "travel_mode": r.mode_travel,
                        "poiID": j.id,
                        "poiName": j.poi_name,
                        "poiLat": j.poi_lat,
                        "poiLon": j.poi_lon,
                        "poiScore": j.poi_score,
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
        print (json.dumps(info, sort_keys=True, indent=4))
        return self.render("admin/routemap.html", info=json.dumps(info), route=r, info2=info2, drive = app.config['JS_OSRM_DRIVE_ADDRESS'], walk = app.config['JS_OSRM_WALK_ADDRESS'], bike = app.config['JS_OSRM_BIKE_ADDRESS'])

    @login_required
    @admin.expose('/create-route', methods=['GET', 'POST'])
    def create_route(self):
        if request.method == "GET":
            return self.render('admin/route_create.html')

        start_pois = request.form.getlist('start_pois_value[]')  # sets start pois list
        start_poi_names = request.form.getlist('start_pois_label')  # sets start poi name list
        end_pois = request.form.getlist('end_pois_value[]')  # sets end pois list
        end_poi_names = request.form.getlist('end_pois_label')
        # sets trip description between stat poi and end poi
        descript_pt = request.form.getlist('input_descriptwopois_pt[]')
        # sets trip description between stat poi and end poi
        descript_en = request.form.getlist('input_descriptwopois_en[]')
        route_status_form = []
        myimage = request.files.getlist('route_image[]')
        for i in range(1, len(start_pois)+1):
            route_status_form.append(request.form['sequence_review_radio'+str(i)])
        
        circle_status = int(request.form['typeRoute_radio'])
        if circle_status is 1:
            route_status_form.append(request.form['sequence_review_radio_circle'])
        else:
            route_status_form.append('0')
        
        #create POI in case it doesn't exist, values besides name are default/placeholder ones
        if start_pois[0] == "":
            poi = POIS(poi_name=start_poi_names[0],
                          poi_lat=40.0,
                          poi_lon=-6.0,
                          category_id=1)
            poi_schedule = POIS_schedule(
                poi_open_h=convert_time_to_decimal("0:0"),
                is_open_or_close=1,
                poi_close_h=convert_time_to_decimal("0:0"),
                poi_vdura=convert_time_to_decimal("0:0"))
            poi.poi_schedule.append(poi_schedule)
            db.session.add(poi)
            db.session.commit()
            db.session.refresh(poi)
            start_pois[0] = int(poi.id)
            
        for index in range(1, len(start_pois)):
            if start_pois[index] == "":
                poi = POIS(poi_name=start_poi_names[index],
                          poi_lat=40.0,
                          poi_lon=-6.0,
                          category_id=1)
                poi_schedule = POIS_schedule(
                    poi_open_h=convert_time_to_decimal("0:0"),
                    is_open_or_close=1,
                    poi_close_h=convert_time_to_decimal("0:0"),
                    poi_vdura=convert_time_to_decimal("0:0"))
                poi.poi_schedule.append(poi_schedule)
                db.session.add(poi)
                db.session.commit()
                db.session.refresh(poi)
                start_pois[index] = int(poi.id)
                end_pois[index-1] = int(poi.id)
                
        if end_pois[len(start_pois)-1] == "":
            poi = POIS(poi_name=end_poi_names[len(end_poi_names)-1],
                          poi_lat=40.0,
                          poi_lon=-6.0,
                          category_id=1)
            poi_schedule = POIS_schedule(
                poi_open_h=convert_time_to_decimal("0:0"),
                is_open_or_close=1,
                poi_close_h=convert_time_to_decimal("0:0"),
                poi_vdura=convert_time_to_decimal("0:0"))
            poi.poi_schedule.append(poi_schedule)
            db.session.add(poi)
            db.session.commit()
            db.session.refresh(poi)
            end_pois[len(start_pois)-1] = int(poi.id) 

        if int(request.form['typeRoute_radio']):  # if route is circle
            start_pois.append(end_pois[len(end_pois) - 1])  # adding last item of list end_pois to the list start_pois
            end_pois.append(start_pois[0])  # adding first item of start_pois to the end_pois
        
        poi_list = list(start_pois)  # holds all input pois list
        if not int(request.form['typeRoute_radio']):  # route is not circle
            poi_list.append(end_pois[len(end_pois) - 1])  # push last item of end_pois list to poi_list
            start_pois.append(start_pois[0])  # add default value
            end_pois.append(start_pois[0])  # add default value
            descript_pt.append("default")  
            descript_en.append("default")
          
                
        poi_list2 = list(poi_list)
        if int(request.form['typeRoute_radio']):
            poi_list2.append(start_pois[0]) # add first start point and last end point to end of poi_list for correct distance and duration if route is circular
        routes = Route(route_name=request.form['input_routename'],
                       mode_travel=request.form['mode_travel'],
                       route_descrip_pt=request.form['geral_routeDescript_pt'],
                       route_descrip_en=request.form['geral_routeDescript_en'],
                       route_distan=get_route_distances(poi_list2, request.form['mode_travel']),
                       route_duration=get_route_duration(poi_list2, request.form['mode_travel']),
                       route_notes=request.form['route_notes'],
                       route_isCircle=circle_status,
                       route_review=int(request.form['route_state_radio']),
                       route_en_review=int(request.form['route_state_radio2']))
        
        imgview = ImageAdminView
        for imgfile in myimage:
            if imgfile and allowed_file(imgfile.filename):
                filename = secure_filename(imgfile.filename)
                # path for a new image, after resize or crop
                path_for_new_img = os.path.join(app.config['UPLOAD_FOLDER'], "copy_" + filename)

                route_img = Images(original_img=filename,
                                 img_descrip=routes.route_name,
                                 copy_img="copy_" + filename,
                                 img_check=True
                                )
                routes.route_image.append(route_img)

                imgfile.save(
                    os.path.join(app.config['UPLOAD_FOLDER'], filename))  # save original image file, uploads folder
                #imgview.resize_crop_img(imgfile, path_for_new_img, size, 'bottom')
                imgview.image_cropper(os.path.join(app.config['UPLOAD_FOLDER'], filename)) # function to crop the images uploaded to the server

        for index, item in enumerate(poi_list):
            seq_pois = SequencePois(pois_list=item,
                                    start_poi_id=start_pois[index],
                                    end_poi_id=end_pois[index],
                                    descrip_start_end_pois_pt=descript_pt[index],
                                    descrip_start_end_pois_en=descript_en[index],
                                    sequence_review=int(route_status_form[index]))
                    
            routes.sequence_pois.append(seq_pois)

        db.session.add(routes)
        db.session.commit()

        flash("The route %s has been created successfully!" % request.form['input_routename'])
        return redirect(url_for('.route'))

    @login_required
    @admin.expose('/edit-route<route_id>', methods=['GET', 'POST'])
    def edit_route(self, route_id):
        """
        :param route_id:  route ID,
        :return:
        """
        route = Route.query.get_or_404(route_id)  # get route from id, can be edited
        
        start_keys = ["start_poi_id", "start_poi_name"]  # start poi label or keys (dict)
        end_keys = ["end_poi_id", "end_poi_name"]  # end poi label

        default_start_poi = []  # default start poi
        default_end_poi = []  # default end poi
        default_route_descript_pt = []  # default trip descript portugues
        default_route_descript_en = []  # default trip descript english
        default_route_count = [1]
        default_route_review = [] # default route review

        start_poi_info = []  # start_poi id and name will be show in dynamic fields
        end_poi_info = []  # end poi id and name will be show in dynamic fields
        route_descript_pt = []  # route description version Pt. will be show in dynamic fields
        route_descript_en = []  # route description version En. will be show in dynamic fields
        route_count =[] # counts the route's position on the list
        route_review =[] #route review for dynamic fields
        rcount = 1 # starting value for counting variable
        route_img_id = [] # list of route image ids
        route_img =[] # list of route images
        
        for item2 in route.route_image:
            route_img_id.append(item2.img_id)
            route_img.append(item2.original_img)
        
        for item in route.sequence_pois:
            query_startpoi = POIS.query.get_or_404(item.start_poi_id)
            
            # append start_poi_id and start poi name to our list, start_poi_info
            start_poi_info.append(dict(zip(start_keys, [query_startpoi.id, query_startpoi.poi_name])))
            
            # append end_poi_id and end_poi_name to list end_poi_info
            query_endpoi = POIS.query.get_or_404(item.end_poi_id)
            
            end_poi_info.append(dict(zip(end_keys, [query_endpoi.id, query_endpoi.poi_name])))
            
            route_descript_pt.append({
                "route_descript_pt": item.descrip_start_end_pois_pt})

            route_descript_en.append({
                "route_descript_en": item.descrip_start_end_pois_en
            })
            
            route_review.append(item.sequence_review)
            route_count.append(rcount)
            rcount += 1
            
        # if route is not circle, we need to remove last items from list start_poi, end_poi, description(default value)
        # its defined on create_poi method.
        if not route.route_isCircle:
            start_poi_info.pop()
            end_poi_info.pop()
            route_descript_pt.pop()
            route_descript_en.pop()
            route_count.pop()

        default_start_poi.append(start_poi_info[0])
        default_end_poi.append(end_poi_info[0])
        default_route_descript_pt.append(route_descript_pt[0])
        default_route_descript_en.append(route_descript_en[0])
        default_route_review.append(route_review[0])
        

        """now we need to remove the first item from the lists start_poi_info, end_poi_info and route_descript, cause
        it all taken by var default_start_poi, default_end_poi and default_route_desscript """
        start_poi_info.pop(0)
        end_poi_info.pop(0)
        route_descript_pt.pop(0)
        route_descript_en.pop(0)
        route_review.pop(0)
        route_count.pop(0)
        

        default_route_info = zip(default_start_poi, default_route_descript_pt, default_route_descript_en,
                                 default_end_poi, default_route_count, default_route_review)
        info_route = list(zip(start_poi_info, route_descript_pt, route_descript_en, end_poi_info, route_count, route_review))
        


        # Handle POST Method
        if request.method == 'POST':
            start_pois = request.form.getlist('start_pois_value[]')  # sets start pois list
            start_poi_names = request.form.getlist('start_pois_label')  # sets start poi name list
            end_pois = request.form.getlist('end_pois_value[]')  # sets end pois list
            end_poi_names = request.form.getlist('end_pois_label')
            descript_pt = request.form.getlist('input_descriptwopois_pt[]')
            descript_en = request.form.getlist('input_descriptwopois_en[]')
            route_status_form = []
            route_status_form.append(request.form['sequence_review_radio'+str(default_route_count[0])])
            for i in range(2, len(start_pois)+1):
                route_status_form.append(request.form['sequence_review_radio'+str(i)])
            if not route.route_isCircle:
                if not int(request.form['typeRoute_radio']):     
                    route_status_form.append('0')
                else:
                    route_status_form.append(request.form['sequence_review_radio_circle'])
            elif route.route_isCircle: 
                if not int(request.form['typeRoute_radio2']):
                    route_status_form.append('0')
                else:
                    route_status_form.append(request.form['sequence_review_radio_circle'])
                
            myimage = request.files.getlist('route_image[]')
            
            
            seq_id_list = [index.id for index in SequencePois.query.with_entities(SequencePois.id).filter(SequencePois.route_id == route.id)]
            
            print(json.dumps(start_pois, sort_keys=True, indent=4))
            print('\n')
            print(json.dumps(end_pois, sort_keys=True, indent=4))
            print('\n')
            print(json.dumps(descript_pt, sort_keys=True, indent=4))
            print(json.dumps(descript_en, sort_keys=True, indent=4))
            
            #create POI in case it doesn't exist
            if start_pois[0] == "":
                poi = POIS(poi_name=start_poi_names[0],
                              poi_lat=40.0,
                              poi_lon=-6.0,
                              category_id=1)
                poi_schedule = POIS_schedule(
                    poi_open_h=convert_time_to_decimal("0:0"),
                    is_open_or_close=1,
                    poi_close_h=convert_time_to_decimal("0:0"),
                    poi_vdura=convert_time_to_decimal("0:0"))
                poi.poi_schedule.append(poi_schedule)

                db.session.add(poi)
                db.session.commit()
                db.session.refresh(poi)
                start_pois[0] = int(poi.id)
                
            for index in range(1, len(start_pois)):
                if start_pois[index] == "":
                    poi = POIS(poi_name=start_poi_names[index],
                              poi_lat=40.0,
                              poi_lon=-6.0,
                              category_id=1)
                    poi_schedule = POIS_schedule(
                        poi_open_h=convert_time_to_decimal("0:0"),
                        is_open_or_close=1,
                        poi_close_h=convert_time_to_decimal("0:0"),
                        poi_vdura=convert_time_to_decimal("0:0"))
                    poi.poi_schedule.append(poi_schedule)
                    db.session.add(poi)
                    db.session.commit()
                    db.session.refresh(poi)
                    start_pois[index] = int(poi.id)
                    end_pois[index-1] = int(poi.id)
                    
            if end_pois[len(start_pois)-1] == "":
                poi = POIS(poi_name=end_poi_names[len(end_poi_names)-1],
                              poi_lat=40.0,
                              poi_lon=-6.0,
                              category_id=1)
                poi_schedule = POIS_schedule(
                    poi_open_h=convert_time_to_decimal("0:0"),
                    is_open_or_close=1,
                    poi_close_h=convert_time_to_decimal("0:0"),
                    poi_vdura=convert_time_to_decimal("0:0"))
                poi.poi_schedule.append(poi_schedule)
                db.session.add(poi)
                db.session.commit()
                db.session.refresh(poi)
                end_pois[len(start_pois)-1] = int(poi.id) 
            
            if not route.route_isCircle:
                if int(request.form['typeRoute_radio']):  # if route is circle
                    start_pois.append(end_pois[len(end_pois) - 1])  # adding last item from list end_pois to the list start_pois
                    end_pois.append(start_pois[0])  # adding first item of start_pois to the end_pois

                poi_list = list(start_pois)  # holds all input pois list
                if not int(request.form['typeRoute_radio']):  # route is not circle
                    poi_list.append(end_pois[len(end_pois) - 1])  # push last item of end_pois list to poi_list
                    start_pois.append(start_pois[0])  # add default value is first item from start poi
                    end_pois.append(start_pois[0])  # add default value is first item from start poi
                    descript_pt.append("default")  #
                    descript_en.append("default")

            else:
                if int(request.form['typeRoute_radio2']):  # if route is circle
                    start_pois.append(end_pois[len(end_pois) - 1])  # adding last item from list end_pois to the list start_pois
                    end_pois.append(start_pois[0])  # adding first item of start_pois to the end_pois

                poi_list = list(start_pois)  # holds all input pois list
                if not int(request.form['typeRoute_radio2']):  # route is not circle
                    poi_list.append(end_pois[len(end_pois) - 1])  # push last item of end_pois list to poi_list
                    start_pois.append(start_pois[0])  # add default value is first item from start poi
                    end_pois.append(start_pois[0])  # add default value is first item from start poi
                    descript_pt.append("default")  #
                    descript_en.append("default")
            if route:
                route.route_name = request.form['input_routename']
                route.mode_travel = request.form['mode_travel']
                if not route.route_isCircle:
                    route.route_isCircle = int(request.form['typeRoute_radio'])
                else:
                    route.route_isCircle = int(request.form['typeRoute_radio2'])
                route.route_descrip_pt = request.form['input_routeDescript_pt']
                route.route_descrip_en = request.form['input_routeDescript_en']
                poi_list2 = list(poi_list)
                if route.route_isCircle:
                    poi_list2.append(start_pois[0])
                    route.route_distan=get_route_distances(poi_list2, request.form['mode_travel'])
                    route.route_duration=get_route_duration(poi_list2, request.form['mode_travel'])
                if len(start_pois)!=len(seq_id_list):
                    if not route.route_isCircle:
                        route.route_distan=get_route_distances(poi_list, request.form['mode_travel'])
                        route.route_duration=get_route_duration(poi_list, request.form['mode_travel'])
                route.route_notes = request.form['input_route_notes']
                route.route_review=int(request.form['route_state_radio'])
                route.route_en_review=int(request.form['route_state_radio2'])
          
                imgview = ImageAdminView
                for imgfile in myimage:
                    if imgfile and allowed_file(imgfile.filename):
                        filename = secure_filename(imgfile.filename)
                        # path for a new image, after resize or crop
                        path_for_new_img = os.path.join(app.config['UPLOAD_FOLDER'], "copy_" + filename)

                        route_img = Images(original_img=filename,
                                           img_descrip=route.route_name,
                                           copy_img="copy_" + filename,
                                           img_check=True
                                          )
                        route.route_image.append(route_img)

                        imgfile.save(
                            os.path.join(app.config['UPLOAD_FOLDER'], filename))  # save original image file, uploads folder
                        imgview.image_cropper(os.path.join(app.config['UPLOAD_FOLDER'], filename)) # function to crop the images uploaded to the server
                
                if len(start_pois)==len(seq_id_list):
                    
                    for index, item in enumerate(route.sequence_pois):
                        try:
                            plist = poi_list[index]
                            pstart = start_pois[index]
                            pfinish = end_pois[index]
                            trip_descript_pt = descript_pt[index]
                            trip_descript_en = descript_en[index]
                            sequence_review = int(route_status_form[index])
                            
                        except IndexError:
                            pstart = ""
                            pfinish = ""
                            plist = ""
                            trip_descript_pt = ""
                            trip_descript_en = ""
                            sequence_review = ""

                        item.pois_list = plist
                        item.start_poi_id = pstart
                        item.end_poi_id = pfinish
                        item.descrip_start_end_pois_pt = trip_descript_pt
                        item.descrip_start_end_pois_en = trip_descript_en
                        item.sequence_review = sequence_review
                        
                else:
                    seqdelete = SequencePois.query.with_entities(SequencePois.id).filter(SequencePois.route_id == route.id).delete()
                    
                    for index, item in enumerate(poi_list):
                        seq_pois = SequencePois(pois_list=item,
                                                start_poi_id=start_pois[index],
                                                end_poi_id=end_pois[index],
                                                descrip_start_end_pois_pt=descript_pt[index],
                                                descrip_start_end_pois_en=descript_en[index],
                                                sequence_review = int(route_status_form[index]))
                        route.sequence_pois.append(seq_pois)
                        
            db.session.commit()
                                        
            
            flash("Route name %s has been updated successfully." % route.route_name)
            return redirect(url_for('.route'))
        
        # Handle GET Method
        else:
            images = zip(route_img_id, route_img)
            return self.render('/admin/route_edit.html', info_route=route, info_route2=info_route,
                               default_value=default_route_info, images=images)

    @login_required
    @admin.expose('/delete-route<route_id>')
    def delete_route(self, route_id):

        route = Route.query.get_or_404(route_id)
        db.session.delete(route)
        db.session.commit()
        flash('The Route %s has been deleted successfully' % route.route_name)
        return redirect(url_for('.route'))

    # Check if the route's name is Unique
    @login_required
    @admin.expose('/check-routename', methods=['GET', 'POST'])
    def check_routename(self):

        state = "true"
        if request.method == 'POST':
            r_name = request.form['input_routename']
            if RouteView.exist_route_name(r_name):
                state = "false"
        return state
    
    # Check if the route's name is Unique, only if it's different from the original
    @login_required
    @admin.expose('/check-routename-edit', methods=['GET', 'POST'])
    def check_routename_edit(self):

        state = "true"
        if request.method == 'POST':
            r_name = request.form['input_routename']
            route_id = request.form['route_id']
            route = Route.query.get_or_404(route_id)
            if r_name == route.route_name:
                state = "true"
            elif RouteView.exist_route_name(r_name):
                state = "false"
        return state

    @staticmethod
    def exist_route_name(input_routename):
        r_name = db.session.query(Route.id).filter(func.lower(Route.route_name) == func.lower(input_routename))
        state = db.session.query(r_name.exists()).scalar()
        return state  # return true, if existed route name.

    @admin.expose('/autocomplete', methods=["GET", "POST"])
    def auto_complete(self):

        column = ["value", "label"]
        result = []
        if request.method == "POST":
            if request.form['key'] == '':
                return ''  # return msg, if POI not existed, create  new POI.
            else:
                query = db.session.query(POIS.poi_name, POIS.id).filter(
                    POIS.poi_name.like('%' + request.form['key'] + '%'))
                for i in query:
                    result.append(dict(zip(column, [i.id, i.poi_name])))
        print (json.dumps(result))
        return jsonify(result)
    
class LogView(AdminAuthenctication_superadmin, AdminAuthenctication_admin, admin.BaseView):
    # Default index view
    @login_required
    @admin.expose('/')
    def log_index(self):
        return redirect(url_for('.log_list'))

    @login_required
    @admin.expose('/view')
    def log_list(self):
        column = ["id", "user_id", "query", "date", "IP"]
        logs = API_Log.query.order_by(API_Log.log_id.desc()).limit(3000).all()

        log_info = []
        for item in logs:
            log_info.append(dict(zip(column, [item.log_id,
                                              item.user_id,
                                              item.log_text,
                                              item.log_date,
                                              item.log_ip])))
        # print(json.dumps(schedule_info, sort_keys=True, indent=4))
        return self.render('admin/logs.html', log_info=log_info)   