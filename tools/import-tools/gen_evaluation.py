#!/usr/bin/env python
# coding: utf-8
import couchdbkit
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
from scielobooks.models import models

db_uri = 'http://localhost:5984'
db_name = 'scielobooks'
rdbms_dsn = 'postgresql+psycopg2://postgres:ash2so4@localhost/scielobooks'

orphan_books = []
integrity_error = []
known_publishers = {}

def get_publisher_or_create(publisher_name):
    if publisher_name not in known_publishers:
        try:
            publisher = session.query(models.Publisher).filter_by(name=publisher_name).one()
        except NoResultFound:
            publisher = models.Publisher(name=publisher_name)
            session.add(publisher)
            session.commit()

        known_publishers[publisher_name] = publisher

    return known_publishers[publisher_name]

def get_monographs():
    try:
       monographs = db.view('scielobooks/books')
    except couchdbkit.ResourceNotFound:
        raise exceptions.NotFound()

    books = []
    for book in monographs:

        b = {'title':book['value']['title'],
             'isbn':book['value']['isbn'],
             'monograph_sbid':book['id'],
             'publisher':get_publisher_or_create(book['value']['publisher']),
             'status':'accepted',
             'is_published':book['value']['visible']}
        books.append(b)

    return books

def create_evaluation(monograph):
    evaluation = models.Evaluation(**monograph)
    session.add(evaluation)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        integrity_error.append(monograph['monograph_sbid'])
    except e:
        session.rollback()
        orphan_books.append((monograph['monograph_sbid'], e.message))


if __name__ == '__main__':
    server = couchdbkit.Server(db_uri)
    db = server.get_or_create_db(db_name)

    engine = sqlalchemy.create_engine(rdbms_dsn, echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()

    for monograph in get_monographs():
        create_evaluation(monograph)

    print 'done'
    print 'Orphan books: ', orphan_books
    print 'Integrity error: ', integrity_error
