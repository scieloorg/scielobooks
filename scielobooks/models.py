import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

Base = declarative_base()

# association table
meeting_evaluation = sqlalchemy.Table('meeting_evaluation', Base.metadata,
    sqlalchemy.Column('meeting_id', sqlalchemy.Integer, sqlalchemy.ForeignKey('meeting.id')),
    sqlalchemy.Column('evaluation_id', sqlalchemy.Integer, sqlalchemy.ForeignKey('evaluation.id'))
)

class Evaluation(Base):
    
    __tablename__ = 'evaluation'
    
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    isbn = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True)
    status = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    subject = sqlalchemy.Column(sqlalchemy.String, )
    publisher_catalog_url = sqlalchemy.Column(sqlalchemy.String, )

    monograph_sbid = sqlalchemy.Column(sqlalchemy.String, )

    publisher_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('publisher.id'))    
    publisher = relationship("Publisher", backref=backref('evaluation', order_by=id))

    def __init__(self, title, isbn, status, subject=None, publisher_catalog_url=None):
        self.title = title
        self.isbn = isbn
        self.status = status

        self.subject = subject
        self.publisher_catalog_url = publisher_catalog_url


class Publisher(Base):
    
    __tablename__ = 'publisher'
    
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True)
    email = sqlalchemy.Column(sqlalchemy.String, )
    publisher_url = sqlalchemy.Column(sqlalchemy.String, )
    
    def __init__(self, name, email=None, publisher_url=None):

        self.name = name

        self.email = email
        self.publisher_url = publisher_url


class Meeting(Base):
    
    __tablename__ = 'meeting'
    
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    
    date = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False, )
    description = sqlalchemy.Column(sqlalchemy.String, )

    # many to many Meeting<->Evaluation
    evaluations = relationship('Evaluation', secondary=meeting_evaluation, backref='meetings')
    
    def __init__(self, date, description=None):

        self.date = date

        self.description = description


