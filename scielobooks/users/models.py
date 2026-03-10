import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import scoped_session, sessionmaker

from datetime import datetime, timedelta
import hashlib

from scielobooks.models import Base
from ..utilities import functions


def _sha256(value):
    if not isinstance(value, bytes):
        value = str(value).encode("utf-8")
    return hashlib.sha256(value).hexdigest()

class User(Base):
    __tablename__ = 'user'
    
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    
    username = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True)
    password = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    password_encryption = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    fullname = sqlalchemy.Column(sqlalchemy.String)
    email = sqlalchemy.Column(sqlalchemy.String)

    creation_date = sqlalchemy.Column(sqlalchemy.DateTime)
    is_active = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False)

    group_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('groups.id'))    
    group = relationship("Group", backref=backref('groups', order_by=id))
    
    identity = sqlalchemy.Column(sqlalchemy.String)
    __mapper_args__ = {'polymorphic_on': identity}
    
    def __init__(self, username, password, group, fullname=None, email=None, is_active=False):
        self.username = username
        self.password = _sha256(password)
        self.password_encryption = 'SHA256'
        self.fullname = fullname
        self.email = email
        self.group = group
        self.is_active = is_active

        self.creation_date = datetime.now()


class Group(Base):    
    __tablename__ = 'groups'
    
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True)
    
    def __init__(self, name,):
        self.name = name


class RegistrationProfile(Base):
    __tablename__ = 'registration_profile'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)

    activation_key = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    expiration_date = sqlalchemy.Column(sqlalchemy.DateTime)
    activation_date = sqlalchemy.Column(sqlalchemy.DateTime)

    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('user.id'))
    user = relationship("User", backref=backref('registration_profile', order_by=id, 
        uselist=False), cascade='all, delete, delete-orphan', single_parent=True)

    def __init__(self, user):
        self.user = user
        self.activation_key = _sha256(user.username)
        self.expiration_date = datetime.now() + timedelta(1)


class AccountRecovery(Base):
    __tablename__ = 'account_recovery'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)

    recovery_key = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    expiration_date = sqlalchemy.Column(sqlalchemy.DateTime)
    recovery_date = sqlalchemy.Column(sqlalchemy.DateTime)

    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('user.id'))
    user = relationship("User", backref=backref('account_recovery', order_by=id,
        uselist=True), cascade='all, delete, delete-orphan', single_parent=True)

    def __init__(self, user):
        self.user = user
        self.recovery_key = _sha256(user.username + str(datetime.now()))
        self.expiration_date = datetime.now() + timedelta(1)
        
