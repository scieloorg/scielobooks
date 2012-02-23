from pyramid.i18n import negotiate_locale_name
from pyramid.response import Response
from pyramid.httpexceptions import HTTPInternalServerError, HTTPFound
from pyramid import exceptions
from pyramid.security import remember, forget
from pyramid.url import route_url
from pyramid.renderers import get_renderer
from pyramid.i18n import TranslationStringFactory
_ = TranslationStringFactory('scielobooks')

import base64
import os

BASE_TEMPLATE = 'scielobooks:templates/base.pt'
HERE = os.path.dirname(__file__)

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

def custom_forbidden_view(request):
    caller_url = base64.b64encode(request.url)
    request.session.flash(_('You are not authorized to access this page. Try logging in before proceed.'))

    return HTTPFound(location=request.route_path('users.login')+'?caller=%s' % caller_url)

def favicon(request):
    try:
        icon = open(os.path.join(HERE, 'static', 'images', 'favicon.ico'))
    except IOError:
        return exceptions.NotFound()

    return Response(content_type='image/x-icon', app_iter=icon)
