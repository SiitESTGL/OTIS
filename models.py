# -*- coding: utf-8 -*-
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash
from app_core import db
import datetime
import time


# --------------------------------------------------------------------
#
#
# --------------------------------------------------------------------

class POIS(db.Model):
    __tablename__ = 'pois'
    id = db.Column(db.Integer, primary_key=True)
    poi_name = db.Column(db.String(64), unique=True)
    poi_lat = db.Column(db.Float, unique=False, nullable=False)
    poi_lon = db.Column(db.Float, unique=False, nullable=False)
    poi_descri_pt_short = db.Column(db.Text)
    poi_descri_en_short = db.Column(db.Text)
    poi_descri_pt_long = db.Column(db.Text)
    poi_descri_en_long = db.Column(db.Text)
    poi_score = db.Column(db.Integer, unique=False, default=1)
    date_poi_created = db.Column(db.DateTime, default=datetime.datetime.now())
    date_poi_updated = db.Column(db.DateTime, default=datetime.datetime.now,
                                 onupdate=datetime.datetime.now())
    poi_source = db.Column(db.String(128))  # Bibliography
    poi_review = db.Column(db.Boolean, default=False)
    poi_en_review = db.Column(db.Boolean, default=False)
    poi_future_review = db.Column(db.Boolean, default=False)
    poi_notes = db.Column(db.Text)
    category_id = db.Column(db.Integer, ForeignKey('category.categ_id', ondelete='CASCADE'), index=True)
    concelho_id = db.Column(db.Integer, ForeignKey('concelhos.conc_id', ondelete='CASCADE'), index=True)
    poi_address = db.Column(db.Text)
    poi_contact = db.relationship('Contact', cascade="all, delete-orphan", backref="pois", lazy="dynamic")
    poi_image = db.relationship('Images', cascade="all, delete-orphan", backref="pois", lazy="dynamic")
    poi_schedule = db.relationship('POIS_schedule', cascade="all, delete-orphan", backref="pois", lazy="dynamic")

    def __init__(self, *args, **kwargs):
        super(POIS, self).__init__(*args, **kwargs)

    def poi_ids(self):
        return self.poi_id

    def __repr__(self):
        return '<Pois %r>' % self.id



class Category(db.Model):  # POI By Category
    __tablename__ = 'category'
    categ_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    categ_name_pt = db.Column(db.String(128))
    categ_name_en = db.Column(db.String(128))
    categ_pois = db.relationship('POIS', backref='category', passive_deletes=True)

    def __init__(self, *args, **kwargs):
        super(Category, self).__init__(*args, **kwargs)

    def __repr__(self):
        return '<category %r' % self.categ_name_en
    
class Concelho(db.Model):  # POI By County
    __tablename__ = 'concelhos'
    conc_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    conc_name = db.Column(db.String(128))
    conc_pois = db.relationship('POIS', backref='concelhos', passive_deletes=True)
    
    def __init__(self, *args, **kwargs):
        super(Concelho, self).__init__(*args, **kwargs)

    def __repr__(self):
        return '<concelhos %r' % self.conc_name


class Images(db.Model):
    __tablename__ = 'images'
    img_id = db.Column(db.Integer, primary_key=True)
    img_descrip = db.Column(db.String(1000), index=True, unique=False)
    original_img = db.Column(db.String(128))
    copy_img = db.Column(db.String(128))
    img_check = db.Column(db.Boolean, unique=False, default=False)
    poi_id = db.Column(db.Integer, ForeignKey('pois.id'), index=True)
    route_id = db.Column(db.Integer, ForeignKey('routes.id'), index=True)
    sequence_id = db.Column(db.Integer, ForeignKey('sequences_pois.id'), index=True)

    def __init__(self, *args, **kwargs):
        super(Images, self).__init__(*args, **kwargs)

    def __repr__(self):
        return '<Images %r>' % self.img_id


class Contact(db.Model):
    __tablename__ = 'contact'
    contact_id = db.Column(db.Integer, primary_key=True)
    telephone = db.Column(db.String(10), unique=False)
    email = db.Column(db.String(64), unique=False)
    website = db.Column(db.String(64))
    poi_id = db.Column(db.Integer, ForeignKey('pois.id'))

    def __init__(self, *args, **kwargs):
        super(Contact, self).__init__(*args, **kwargs)  # call the parent constructor

    def __repr__(self):
        return '<Poi Contact: %r>' % self.telephone


class POIS_schedule(db.Model):
    __tablename__ = 'pois_schedule'
    id = db.Column(db.Integer, primary_key=True)
    poi_id = db.Column(db.Integer, ForeignKey('pois.id'))
    poi_vdura = db.Column(db.Integer, unique=False)
    poi_open_h = db.Column(db.Integer, unique=False)
    poi_close_h = db.Column(db.Integer, unique=False)
    is_open_or_close = db.Column(db.Boolean, unique=False)

    def __init__(self, *args, **kwargs):
        super(POIS_schedule, self).__init__(*args, **kwargs)

    def __repr__(self):
        return '<Poi_schedule %r>' % self.POI_Schedule_id


class POIS_distances(db.Model):
    __tablename__ = 'pois_distances'
    id = db.Column(db.Integer, primary_key=True)
    start_poi_id = db.Column(db.Integer, index=True, unique=False)
    end_poi_id = db.Column(db.Integer, index=True, unique=False)
    trip_duration = db.Column(db.Integer, index=True, unique=False)
    trip_distance = db.Column(db.Integer, index=True, unique=False)
    trip_description = db.Column(db.String, index=True, unique=False)
    trip_duration_walk = db.Column(db.Integer, index=True, unique=False)
    trip_distance_walk = db.Column(db.Integer, index=True, unique=False)

    def __init__(self, *args, **kwargs):
        super(POIS_distances, self).__init__(*args, **kwargs)

    def __repr__(self):
        return '<POIS_distances %r>' % self.Start_POI_id


class Route(db.Model):
    __tablename__ = "routes"
    id = db.Column(db.Integer, primary_key=True)
    route_name = db.Column(db.String(64), index=True, unique=True)
    mode_travel = db.Column(db.String(64), index=True, nullable=False,
                            unique=False)  # [walking, driving, bicycling]
    route_descrip_pt = db.Column(db.Text, index=True, unique=False)
    route_descrip_en = db.Column(db.Text, index=True, unique=False)
    route_distan = db.Column(db.Float, index=True, unique=False, default=0)
    route_duration = db.Column(db.Integer, index=True, unique=False, default=0)
    route_isCircle = db.Column(db.Boolean, unique=False)
    date_route_created_ = db.Column(db.DateTime, default=datetime.datetime.now)
    date_route_updated = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    route_notes = db.Column(db.Text)
    route_file = db.Column(db.String(64), index=True)
    route_review = db.Column(db.Boolean, default=False)
    route_en_review = db.Column(db.Boolean, default=False)
    route_score = db.Column(db.Integer, default = 1)
    sequence_pois = relationship("SequencePois", cascade="all, delete-orphan", backref="routes", lazy="dynamic")
    route_image = db.relationship('Images', cascade="all, delete-orphan", backref="routes", lazy="dynamic")


    # Constructor----------------------------------------------------------------------------------------------------+
    def __init__(self, *args, **kwargs):
        super(Route, self).__init__(*args, **kwargs)

    def is_circle_route(self, inval):
        if "circle" == inval:
            return True

    def __repr__(self):
        return '<Route %r %r>' % (self.id, [poi.pois_list for poi in self.sequence_pois])


# class Route_Sequence
class SequencePois(db.Model):
    __tablename__ = "sequences_pois"
    id = db.Column(db.Integer, primary_key=True)
    route_id = db.Column(db.Integer, ForeignKey('routes.id'))
    pois_list = db.Column(db.String(1000), index=True)
    start_poi_id = db.Column(db.Integer, index=True, default=1)
    end_poi_id = db.Column(db.Integer, index=True, default=1)
    descrip_start_end_pois_pt = db.Column(db.Text, index=True, unique=False, default="")
    descrip_start_end_pois_en = db.Column(db.Text, index=True, default="")
    sequence_review = db.Column(db.Boolean, unique=False, default = 1)
    sequence_image = db.relationship('Images', cascade="all, delete-orphan", backref="sequence", lazy="dynamic")


    def __init__(self, *args, **kwargs):
        super(SequencePois, self).__init__(*args, **kwargs)

    def __repr__(self):
        return "Routes %r" % self.pois_list


class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column('user_id', db.Integer, primary_key=True)
    username = db.Column('username', db.String(255), unique=True, index=True)
    password = db.Column('password', db.String(32))
    email = db.Column('email', db.String(60), unique=True, index=True)
    registered_on = db.Column('registered_on', db.DateTime)
    active = db.Column(db.Boolean, default=False)
    admin = db.Column(db.Boolean, default=False)
    super_admin = db.Column(db.Boolean, default=False)
    user_key = db.relationship('API_Key', cascade="all, delete-orphan", backref="users", lazy="dynamic")
    user_logs = db.relationship('API_Log', cascade="all, delete-orphan", backref="users", lazy="dynamic")
    '''roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))'''

    def __init__(self, username, password, email, admin=0, superadmin=0 ):
        self.username = username
        self.password = password
        self.email = email
        self.admin = admin
        self.super_admin = superadmin
        self.registered_on = datetime.datetime.now()


    @staticmethod
    def make_password(plaintext):
        return generate_password_hash(plaintext)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)

    @classmethod
    def create(cls, username, password, **kwargs):
        return User(username=username,
                    password = User.make_password(password), **kwargs)

    @staticmethod
    def authenticate(username, password):
        user = User.query.filter(User.username == username).first()
        if user and user.check_password(password):
            return user
        return False


    def is_authenticated(self):
        return True

    def is_admin(self):
        return self.admin

    def is_super_admin(self):
        return self.super_admin

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.user_id)

    def __repr__(self):
        return '<User %r>' % self.username
    
class API_Key(db.Model):
    __tablename__ = 'API_keys'
    key_id = db.Column('key_id', db.Integer, primary_key=True)
    key = db.Column('key_string', db.String(64), unique=True)
    user_id = db.Column('user_id', db.Integer, ForeignKey('users.user_id'))
    valid = db.Column('key_valid', db.Boolean, default=True)
    quarantine = db.Column('key_quarantine', db.Boolean, default=False)

    
class API_Log(db.Model):
    __tablename__ = 'API_log'
    log_id = db.Column('log_id', db.Integer, primary_key=True)
    user_id = db.Column('user_id', db.Integer, ForeignKey('users.user_id'))
    log_text = db.Column('log_text', db.Text)
    log_date = db.Column('log_date', db.Float, default=func.now())
    log_ip = db.Column('log_ip', db.String(15))
