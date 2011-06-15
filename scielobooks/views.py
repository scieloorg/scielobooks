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

def attach(request):
    pass