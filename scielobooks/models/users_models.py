import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import scoped_session, sessionmaker

from datetime import datetime
from Crypto.Hash import SHA256

from scielobooks.models import Base
from .models import Publisher 

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

    group_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('group.id'))    
    group = relationship("Group", backref=backref('group', order_by=id))
    
    identity = sqlalchemy.Column(sqlalchemy.String)
    __mapper_args__ = {'polymorphic_on': identity}
    
    def __init__(self, username, password, fullname=None, email=None):
        self.username = username
        self.password = SHA256.new(password).hexdigest()
        self.password_encryption = 'SHA256'
        self.fullname = fullname
        self.email = email

        self.creation_date = datetime.now()


class Admin(User):

    __mapper_args__ = {'polymorphic_identity': 'admin'}

    def __init__(self, username, password, fullname=None, email=None):
        super(Admin,self).__init__(username,password,fullname,email)


class Editor(User):

    publisher_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('publisher.id'))    
    publisher = relationship("Publisher", )

    __mapper_args__ = {'polymorphic_identity': 'editor'}
    
    def __init__(self, username, password, publisher, fullname=None, email=None):
        super(Editor,self).__init__(username,password,fullname,email)    
        self.publisher = publisher


class Group(Base):    
    __tablename__ = 'group'
    
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True)
    
    def __init__(self, name, email=None, publisher_url=None):
        self.name = name

