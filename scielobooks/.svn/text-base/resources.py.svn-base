from pyramid.security import Allow, Everyone

class Root(object):
    __acl__ = [ (Allow, Everyone, 'view'),
                (Allow, 'group:editors', 'list') ]
    def __init__(self, request):
        self.request = request
