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

BASE_TEMPLATE = 'scielobooks:templates/base.pt'

def signup(request):
    localizer = get_localizer(request)
    main = get_renderer(BASE_TEMPLATE).implementation()
    publisher = request.rel_db_session.query(models.Publisher.name_slug, models.Publisher.name).all()
    signup_form = SignupForm.get_form(localizer,publisher)

    if 'submit' in request.POST:
                
        controls = request.POST.items()
        try:
            appstruct = signup_form.validate(controls)
        except deform.ValidationFailure, e:
            
            return {'content':e.render(), 
                    'main':main, 
                    'form_title':_('Signup'),
                    }

        del(appstruct['__LOCALE__'])

        appstruct['publisher'] = request.rel_db_session.query(models.Publisher).filter_by(name_slug=appstruct['publisher']).one()
        editor = users.Editor(**appstruct)
        request.rel_db_session.add(editor)

        try:
            request.rel_db_session.commit()
        except IntegrityError:
            request.rel_db_session.rollback()
            request.session.flash(_('This username already exists.'))
            return {'content':signup_form.render(appstruct),
                    'main':main,
                    'form_title':'Signup',
                    }
        request.session.flash(_('Successfully added.'))
        return HTTPFound(location=request.route_path('staff.panel'))

    return {'content':signup_form.render(),
            'form_title': _('Signup'),
            'main':main,
            }