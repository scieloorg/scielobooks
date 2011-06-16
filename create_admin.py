
from scielobooks.models import users_models
from sqlalchemy.orm import sessionmaker
import sqlalchemy

engine = sqlalchemy.create_engine('sqlite:///database.db', echo=True)
Session = sessionmaker(bind=engine)
session = Session()

group = users_models.Group('admin')
admin = users_models.User('admin','123456',group)

session.add(group)
session.add(admin)

session.commit()
