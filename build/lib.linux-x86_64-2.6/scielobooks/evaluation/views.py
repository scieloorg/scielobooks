from pyramid.view import view_config
from pyramid.response import Response
from pyramid import exceptions
from pyramid.url import route_url
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

from .models import Evaluation, Monograph

BASE_TEMPLATE = 'scielobooks:templates/base.pt'
MIMETYPES = {
    'application/pdf':'pdf',
    'application/epub':'epub',
}

def main_fields(composite_property):
    if isinstance(composite_property, list):
        return [subfield['_'] for subfield in composite_property]
    else:
        return composite_property['_']

def book_details(request):
    sbid = request.matchdict['sbid']
    try:
        evaluation = request.db.get(sbid)
    except couchdbkit.ResourceNotFound:
        raise exceptions.NotFound()
    if evaluation['TYPE'] != 'Evaluation':
        raise exceptions.NotFound()

    try:
        monograph = request.db.get(evaluation['monograph'])
    except couchdbkit.ResourceNotFound:
        raise exceptions.NotFound()

    if 'creators' in monograph:
        creators = [dict(creator) for creator in monograph['creators']]
    else:
        creators = []

    document = monograph

    document.update({
        'cover_url': '',
        'breadcrumb': {'home':request.registry.settings['solr_url'],},
        'creators': main_fields(creators),
    })

    main = get_renderer(BASE_TEMPLATE).implementation()

    return {'document':document,
            'main':main}

def books_list(request):
    try:
       books = request.db.view('scielobooks/evaluation')
    except couchdbkit.ResourceNotFound:
        raise exceptions.NotFound()

    documents = {}
    for book in books:
        if book['key'] not in documents:
            documents[book['key']] = []

        book_meta = {'title':book['value']['title'],
                     'details_url':request.route_path('evaluation.book_details',
                                                      sbid=book['id']),
                     }
        documents[book['key']].append(book_meta)

    main = get_renderer(BASE_TEMPLATE).implementation()

    return {'documents': documents,
            'total_documents': len(books),
            'main':main}

def new_book(request):
    evaluation_schema = Evaluation.get_schema()
    evaluation_form = deform.Form(evaluation_schema, buttons=('submit',))

    main = get_renderer(BASE_TEMPLATE).implementation()

    if 'submit' in request.POST:
        controls = request.POST.items()
        try:
            appstruct = evaluation_form.validate(controls)
        except deform.ValidationFailure, e:
            return {'form':e.render(), 'main':main}

        evaluation = Evaluation.from_python(appstruct)
        monograph = Monograph()
        monograph_id = monograph.save(request.db)
        evaluation.monograph = monograph_id
        evaluation_id = evaluation.save(request.db)

        request.session.flash('Adicionado com sucesso.')

        return {'form':None, 'main':main}

    return {'form':evaluation_form.render(),
            'main':main}