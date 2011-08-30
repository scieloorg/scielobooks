from sqlalchemy.orm.exc import NoResultFound
from users import models as user_models

def groupfinder(userid, request):
    try:
        user = request.rel_db_session.query(user_models.User).filter_by(id=userid).one()
    except NoResultFound:
        return []

    return [user.group.name]