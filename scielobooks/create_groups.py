
import sqlalchemy
from sqlalchemy.orm import sessionmaker

from models.users_models import Group

engine = sqlalchemy.create_engine('sqlite:///../database.db', echo=False)
Session = sessionmaker(bind=engine)
session = Session()

groups = ['admin','editor']

for g in groups:
    gr = Group(g)
    session.add(gr)

session.commit()
