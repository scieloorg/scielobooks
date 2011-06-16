import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import scoped_session, sessionmaker
from datetime import datetime

from scielobooks.models import Base

from ..utilities import functions


class Evaluation(Base):
    __tablename__ = 'evaluation'
    
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    isbn = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True)
    status = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    subject = sqlalchemy.Column(sqlalchemy.String, )
    publisher_catalog_url = sqlalchemy.Column(sqlalchemy.String, )
    creation_date = sqlalchemy.Column(sqlalchemy.DateTime, )

    monograph_sbid = sqlalchemy.Column(sqlalchemy.String, )
    is_published = sqlalchemy.Column(sqlalchemy.Boolean, )

    publisher_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('publisher.id'))    
    publisher = relationship("Publisher", backref=backref('evaluation', order_by=id))

    meeting_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('meeting.id'))
    meeting = relationship("Meeting", backref=backref('evaluation', order_by=id))

    def __init__(self, title, isbn, status, subject=None, publisher_catalog_url=None, is_published=False):
        self.title = title
        self.isbn = isbn
        self.status = status

        self.creation_date = datetime.now()
        
        self.subject = subject
        self.publisher_catalog_url = publisher_catalog_url
        self.is_published = is_published


class Publisher(Base):    
    __tablename__ = 'publisher'
    
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True)
    email = sqlalchemy.Column(sqlalchemy.String, )
    publisher_url = sqlalchemy.Column(sqlalchemy.String, )
    name_slug = sqlalchemy.Column(sqlalchemy.String, unique=True)
    
    def __init__(self, name, email=None, publisher_url=None):
        self.name = name
        self.name_slug = functions.slugify(name)

        self.email = email
        self.publisher_url = publisher_url
    
    def as_dict(self):
        return {'name': self.name,
                'email': self.email,
                'publisher_url': self.publisher_url,
                }


class Meeting(Base):    
    __tablename__ = 'meeting'
    
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    
    date = sqlalchemy.Column(sqlalchemy.Date, nullable=False, )
    description = sqlalchemy.Column(sqlalchemy.String, )

        
    def __init__(self, date, description=None):
        self.date = date

        self.description = description