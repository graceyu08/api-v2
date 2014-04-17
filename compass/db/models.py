"""Database model"""
from copy import deepcopy
from datetime import datetime
from hashlib import md5
import simplejson as json


from sqlalchemy import Table
from sqlalchemy import Column, Integer, String
from sqlalchemy import Float, Enum, DateTime, ForeignKey, Text, Boolean
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.types import TypeDecorator


from flask.ext.login import UserMixin
from itsdangerous import URLSafeTimedSerializer


BASE = declarative_base()
#TODO(grace) SECRET_KEY should be generated when installing compass
#and save to a config file or DB
SECRET_KEY = "abcd"

#This is used for generating a token by user's ID and
#decode the ID from this token
login_serializer = URLSafeTimedSerializer(SECRET_KEY)


class JSONEncodedDict(TypeDecorator):
    """Represents an immutable structure as a json-encoded string"""

    impl = Text

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


class TimestampMixin(object):
    created_at = Column(DateTime, default=lambda: datetime.now())
    updated_at = Column(DateTime, onupdate=lambda: datetime.now())


class HelperMixin(object):
    def to_dict(self):
        dict_info = self.__dict__.copy()
        dict_info.pop('_sa_instance_state')
        return dict_info


class User(BASE, UserMixin, HelperMixin):
    """User table"""
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    email = Column(String(80), unique=True)
    password = Column(String(225))
    firstname = Column(String(80))
    lastname = Column(String(80))
    is_admin =  Column(Boolean, default=False)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now())
    last_login_at = Column(DateTime, default=lambda: datetime.now())

    def __init__(self, email, password, **kwargs):
        self.email = email
        self.password = self._set_password(password)

    def __repr__(self):
        return '<User name: %s>' % self.email

    def _set_password(self, password):
        return self._hash_password(password)

    def get_password(self):
        return self.password

    def valid_password(self, password):
        return self.password == self._hash_password(password)

    def get_auth_token(self):
        return login_serializer.dumps(self.id)

    def is_active(self):
        return self.active

    def _hash_password(self, password):
        return md5(password).hexdigest()


class Permission(BASE):
    """Permission table"""
    __tablename__ = 'permission'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True)
    alias = Column(String(100))

    def __init__(self, name, alias=None):
        self.name = name
        if alias:
            self.alias = alias


user_permission = Table('user_permission', BASE.metadata,
    Column('user_id', Integer, ForeignKey('user.id')),
    Column('permission_id', Integer, ForeignKey('permission.id'))
)
