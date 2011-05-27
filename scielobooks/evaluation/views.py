from pyramid.view import view_config
from pyramid.response import Response
from pyramid import exceptions
from pyramid.url import route_url, static_url
from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import get_renderer
from pyramid.i18n import TranslationStringFactory
_ = TranslationStringFactory('scielobooks')

from forms import EvaluationForm

import couchdbkit
import urllib2
import json
import deform
import Image
import StringIO
import os
import uuid
import colander
#FIXME
import isis
import models

from .models import Evaluation, Monograph, Part

BASE_TEMPLATE = 'scielobooks:templates/base.pt'
MIMETYPES = {
    'application/pdf':'pdf',
    'application/epub':'epub',
}
COVER_SIZES = {
    # id:(width, height),
    'sz1':(160, 160),
    'sz2':(180, 180),
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

    if 'creators' in monograph and isinstance(monograph.get('creators',None), tuple):
        creators = main_fields([dict(creator) for creator in monograph['creators']])
    else:
        creators = [creator for creator in monograph['creators']]

    document = monograph
    
    document.update({
        'cover_url': request.route_path('evaluation.cover', sbid=monograph['_id'], size='sz1'),
        'breadcrumb': {'home':request.registry.settings['solr_url'],},
        'creators': creators,        
    })

    editorial_decision = evaluation.get('editorial_decision', {}).get('filename', None)
    if editorial_decision is not None:
        editorial_decision_url = static_url('scielobooks:database/%s/%s', request) % (evaluation['_id'], editorial_decision)
        document.update({'editorial_decision_url':editorial_decision_url})
    
    toc = evaluation.get('toc', {}).get('filename', None)
    if toc is not None:
        toc_url = static_url('scielobooks:database/%s/%s', request) % (evaluation['_id'], toc)
        document.update({'toc_url':toc_url})

    publisher_url = evaluation.get('publisher_url', None)
    if publisher_url is not None:        
        document.update({'publisher_url':publisher_url})
    

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

    monograph_form = EvaluationForm.get_form()

    main = get_renderer(BASE_TEMPLATE).implementation()

    if 'submit' in request.POST:
   
        controls = request.POST.items()
        try:
            appstruct = monograph_form.validate(controls)
        except deform.ValidationFailure, e:
            return {'monograph_form':e.render(), 'main':main}
        
        monograph = Monograph.from_python(appstruct)
        
        if 'sbid' in request.matchdict: #edit document

            monograph.evaluation = request.db.get(monograph._id)['evaluation']
            monograph.save(request.db)
            
            evaluation = Evaluation.get(request.db, monograph.evaluation)

            evaluation.publisher = monograph.publisher
            evaluation.title = monograph.title

            if appstruct['toc'] is not None:
                evaluation.toc = appstruct['toc']
            if appstruct['editorial_decision'] is not None:
                evaluation.editorial_decision = appstruct['editorial_decision']
            if appstruct['publisher_url'] is not None:
                evaluation.publisher_url = appstruct['publisher_url']

            evaluation.save(request.db)

            request.session.flash('Atualizado com sucesso.')
        else: #new document
            monograph.save(request.db)

            evaluation = Evaluation.from_python(appstruct)
            evaluation.monograph = monograph._id           
            evaluation.save(request.db)

            monograph.evaluation = evaluation._id
            monograph.save(request.db)

            request.session.flash('Adicionado com sucesso.')        

        return {'monograph_form':None,
                'main':main}
    
    if 'sbid' in request.matchdict:
        monograph_id = request.db.get(request.matchdict['sbid'])['monograph']
        monograph = Monograph.get(request.db, monograph_id)
        appstruct = monograph.to_python()

        evaluation = Evaluation.get(request.db, monograph.evaluation, controls=False)
             
        appstruct.update(evaluation.to_python())

        return {'monograph_form':monograph_form.render(appstruct),
                'main':main}
    
    return {'monograph_form':monograph_form.render(),
            'main':main}

def cover(request):
    sbid = request.matchdict['sbid']
    size = request.matchdict['size']

    try:
        evaluation = request.db.get(sbid)
    except couchdbkit.ResourceNotFound:
        raise exceptions.NotFound()

    #FIXME: Restrict for type = Evaluation (need to think about the data entry form)
    # if evaluation['TYPE'] != 'Evaluation':
    #     raise exceptions.NotFound()

    try:
        attach_name = evaluation['cover']['filename']
    except KeyError:
        raise exceptions.NotFound()

    if size in COVER_SIZES:
        img_size = COVER_SIZES[size]
    else:
        size = 'sz1'
        img_size = COVER_SIZES['sz1']

    filepath = '/tmp/cover-%s.%s.JPEG' % (sbid, size)
    
    cover_url = static_url('scielobooks:database/%s/%s', request) % (sbid, attach_name)
    try:
        img = urllib2.urlopen(cover_url.replace(' ', '%20'))#FIXME: urlencode must be handled more seriously
        img_thumb = Image.open(StringIO.StringIO(img.read()))
        img_thumb.thumbnail(img_size, Image.ANTIALIAS)
        img_thumb.save(filepath, 'JPEG')

        return Response(body=open(filepath).read(), content_type='image/jpeg')
    except urllib2.HTTPError:
        img = urllib2.urlopen(static_url('scielobooks:static/images/fakecover.jpg', request))

        return Response(body=img.read(), content_type='image/jpeg')

def parts_list(request):
    monograph_id = request.matchdict['sbid']
    try:
       parts = request.db.view('scielobooks/monographs_and_parts', include_docs=True, key=[monograph_id, 1])
    except couchdbkit.ResourceNotFound:
        raise exceptions.NotFound()

    documents = {}
    for part in parts:
        part_meta = {'title':part['doc']['title'],
                     'order':part['doc']['order'],
                     'creators':part['doc']['creators'],
                     'edit_url':request.route_path('evaluation.edit_part', sbid=monograph_id, part_id=part['id'])}

        documents[part['id']] = part_meta    
    
    main = get_renderer(BASE_TEMPLATE).implementation()

    return {'documents': documents,
            'main':main}

def new_part(request):    
    monograph_id = request.matchdict['sbid']

    part_schema = Part.get_schema()
    part_form = deform.Form(part_schema, buttons=('submit',))

    main = get_renderer(BASE_TEMPLATE).implementation()

    if 'submit' in request.POST:
   
        controls = request.POST.items()
        try:
            appstruct = part_form.validate(controls)
        except deform.ValidationFailure, e:
            return {'part_form':e.render(), 'main':main}
                
        part = Part.from_python(appstruct)
        part.monograph = monograph_id

        part.save(request.db)
        request.session.flash('Adicionado com sucesso.')
    
        return {'part_form':None,
                'main':main}

    if 'part_id' in request.matchdict:
        part = Part.get(request.db, request.matchdict['part_id'])
        
        return {'part_form':part_form.render(part.to_python()),
                'main':main}    

    return {'part_form':part_form.render(),
            'main':main}