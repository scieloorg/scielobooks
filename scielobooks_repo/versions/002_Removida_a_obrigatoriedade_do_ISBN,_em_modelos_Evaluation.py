from sqlalchemy import *
from migrate import *


def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    evaluation = Table('evaluation', meta, autoload=True)
    evaluation.columns['isbn'].alter(nullable=True)


def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    evaluation = Table('evaluation', meta, autoload=True)
    evaluation.columns['isbn'].alter(nullable=False)