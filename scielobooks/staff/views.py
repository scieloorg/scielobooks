from pyramid.view import view_config
from pyramid.response import Response
from pyramid import exceptions
from pyramid.url import route_url, static_url
from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import get_renderer
from pyramid.i18n import TranslationStringFactory
_ = TranslationStringFactory('scielobooks')

import couchdbkit
import urllib2
import json
import deform
import Image
import StringIO
import os
import uuid
import colander

BASE_TEMPLATE = 'scielobooks:templates/base.pt'


def staff_panel(request):
    try:
       books = request.db.view('evaluation/staff').all()
    except couchdbkit.ResourceNotFound:
        raise exceptions.NotFound()

    main = get_renderer(BASE_TEMPLATE).implementation()

    # import pdb; pdb.set_trace()
    return {'documents': {'books':books},
            'total_documents': len(books),
            'main':main}

