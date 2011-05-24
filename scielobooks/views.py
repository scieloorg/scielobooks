from pyramid.i18n import negotiate_locale_name
from pyramid.response import Response
from pyramid.httpexceptions import HTTPInternalServerError, HTTPFound
from pyramid.security import remember, forget
from pyramid.url import route_url
from pyramid.renderers import get_renderer

from .security import USERS

BASE_TEMPLATE = 'scielobooks:templates/base.pt'

def set_language(request):
    if request.POST:
        local_name = negotiate_locale_name(request)
        resp = Response()
        resp.headers = {'Location': request.referrer}
        resp.status = '302'
        resp.set_cookie('language', local_name)

        return resp
    else:
        return HTTPInternalServerError()

def login(request):
    login_url = route_url('general.login', request)
    referrer = request.url
    if referrer == login_url:
        referrer = '/' # never use the login form itself as came_from
    came_from = request.params.get('came_from', referrer)
    message = ''
    login = ''
    password = ''

    main = get_renderer(BASE_TEMPLATE).implementation()

    if 'form.submitted' in request.params:
        login = request.params['login']
        password = request.params['password']
        if USERS.get(login) == password:
            headers = remember(request, login)
            return HTTPFound(location = came_from,
                             headers = headers)
        message = 'Failed login'

    return dict(
        message = message,
        url = request.application_url + '/login',
        came_from = came_from,
        login = login,
        password = password,
        main = main,
        )

def logout(request):
    headers = forget(request)
    return HTTPFound(location = route_url('general.login', request),
                     headers = headers)

def attach(request):
    pass