from pyramid.security import Allow, Everyone

class RootFactory(object):
    __acl__ = [ (Allow, Everyone, 'view'),
                (Allow, 'editor', 'editors'),
                (Allow, 'admin', ('editors','admin')),
              ]
    def __init__(self, request):
        pass
