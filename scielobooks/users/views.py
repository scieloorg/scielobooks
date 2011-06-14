# coding: utf-8

from pyramid.view import view_config
from pyramid.response import Response
from pyramid import exceptions
from pyramid.url import route_url, static_url
from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import get_renderer
from pyramid.i18n import get_localizer
from pyramid.i18n import TranslationStringFactory
_ = TranslationStringFactory('scielobooks')

from sqlalchemy.exc import IntegrityError
from datetime import date

from forms import SignupForm
from ..models import users_models as users
from ..models import models


import json
import deform
import colander


def signup(request):
    localizer = get_localizer(request)
    publishers = request.rel_db_session.query(models.Publisher.name_slug, models.Publisher.name).all()

    return Response(SignupForm.get_form(localizer, publisher).render())