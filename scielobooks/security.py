
from users import models as user_models

def groupfinder(userid, request):
    
    USERS = request.rel_db_session.query(user_models.User.id).all()
    if userid in [user[0] for user in USERS]:
        group_name = request.rel_db_session.query(user_models.User).get(userid).group.name
        
        return [group_name]