from pyramid.request import Request
from pyramid.decorator import reify

class MyRequest(Request):
    @reify
    def rel_db_session(self):
        maker = self.registry.settings['rel_db.sessionmaker']
        return maker()
