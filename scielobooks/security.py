
from models import users_models as users 

def groupfinder(userid, request):
    
    USERS = request.rel_db_session.query(users.User.id).all()
    if userid in [user[0] for user in USERS]:
        group_name = request.rel_db_session.query(users.User).get(userid).group.name
        
        return [group_name]