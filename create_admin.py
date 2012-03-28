#!/usr/bin/env python
# coding: utf-8
'''
Script to load essencial data and create the default "admin" user.
This script should be called once right after the system is deployed.
'''

from scielobooks.users import models as users_models
from scielobooks.models import models
from sqlalchemy.orm import sessionmaker
import sqlalchemy
from sqlalchemy.exc import IntegrityError

engine = sqlalchemy.create_engine('postgresql+psycopg2://postgres:123456@localhost:5432/scielobooks', echo=True)
Session = sessionmaker(bind=engine)
session = Session()

group_admin = users_models.Group('admin')
session.add(group_admin)

try:
    session.commit()
except IntegrityError:
    session.rollback()
    group_admin = session.query(users_models.Group).filter_by(name='admin').one()

admin = models.Admin('admin', '123456', group_admin, is_active=True)
reg_profile = users_models.RegistrationProfile(admin)
reg_profile.activation_key = 'ACTIVATED'

session.add(admin)
session.add(reg_profile)

session.commit()
print 'done'