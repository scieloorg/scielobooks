import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import scoped_session, sessionmaker

from datetime import datetime, timedelta
from Crypto.Hash import SHA256

from scielobooks.models import Base
from ..utilities import functions

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
        self.password = SHA256.new(password).hexdigest()
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
        self.activation_key = SHA256.new(user.username).hexdigest()
        self.expiration_date = datetime.now() + timedelta(1)
        