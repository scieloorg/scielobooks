# coding: utf-8

from pyramid.view import view_config
from pyramid.response import Response
from pyramid import exceptions
from pyramid.url import route_url, static_url
from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import get_renderer
from sqlalchemy.exc import IntegrityError
from pyramid.i18n import TranslationStringFactory
_ = TranslationStringFactory('scielobooks')


from forms import MonographForm, PublisherForm, EvaluationForm
from ..models import models as rel_models

import couchdbkit
import urllib2
import json
import deform
import Image
import StringIO
import os
import uuid
import colander

from .models import Evaluation, Monograph, Part

BASE_TEMPLATE = 'scielobooks:templates/base.pt'
MIMETYPES = {
    'application/pdf':'pdf',
    'application/epub':'epub',
}

def edit_book(request):    

    monograph_form = MonographForm.get_form()

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
        # else: #new document
        #     monograph.save(request.db)

        #     evaluation = Evaluation.from_python(appstruct)
        #     evaluation.monograph = monograph._id           
        #     evaluation.save(request.db)

        #     monograph.evaluation = evaluation._id
        #     monograph.save(request.db)

        #     request.session.flash('Adicionado com sucesso.')        

        return {'monograph_form':None,
                'main':main}
    
    if 'sbid' in request.matchdict:        
        monograph = Monograph.get(request.db, request.matchdict['sbid'])
        appstruct = monograph.to_python()

        evaluation = Evaluation.get(request.db, monograph.evaluation, controls=False)
             
        appstruct.update(evaluation.to_python())

        return {'monograph_form':monograph_form.render(appstruct),
                'main':main}
    
    return {'monograph_form':monograph_form.render(),
            'main':main}

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
                     'edit_url':request.route_path('staff.edit_part', sbid=monograph_id, part_id=part['id'])}

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

def book_details(request):
    sbid = request.matchdict['sbid']
    try:
        monograph = request.db.get(sbid)
    except couchdbkit.ResourceNotFound:
        raise exceptions.NotFound()
    if monograph['TYPE'] != 'Monograph':
        raise exceptions.NotFound()
        
    try:
        evaluation = request.db.get(monograph['evaluation'])
    except couchdbkit.ResourceNotFound:
        raise exceptions.NotFound()


    if 'creators' in monograph and isinstance(monograph.get('creators',None), tuple):
        creators = main_fields([dict(creator) for creator in monograph['creators']])
    else:
        creators = [creator for creator in monograph['creators']]

    document = monograph
    
    document.update({
        'cover_url': request.route_path('evaluation.cover', sbid=sbid, size='sz1'),
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


def panel(request):

    try:
       books = request.db.view('scielobooks/staff')
    except couchdbkit.ResourceNotFound:
        raise exceptions.NotFound()

    main = get_renderer(BASE_TEMPLATE).implementation()

    return {'documents': {'books':books},
            'total_documents': len(books),
            'main':main}

def new_publisher(request):

    main = get_renderer(BASE_TEMPLATE).implementation()
    
    publisher_form = PublisherForm.get_form()
    
    if 'submit' in request.POST:

        controls = request.POST.items()
        try:
            appstruct = publisher_form.validate(controls)
        except deform.ValidationFailure, e:
            return {'publisher_form':e.render(), 'main':main}
    
        session = request.rel_db_session

        if 'slug' in request.matchdict: 
            #edit
            slug = request.matchdict.get('slug')
            publisher = session.query(rel_models.Publisher).filter_by(name_slug=slug).one()
            
            publisher.email = appstruct['email']
            publisher.publisher_url = appstruct['publisher_url']
    
        else:
            #new
            publisher = rel_models.Publisher(**appstruct)

        session.add(publisher)
            
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            request.session.flash(u'Esse registro já existe.')
            return {'publisher_form':publisher_form.render(appstruct), 'main':main}

        request.session.flash('Adicionado com sucesso.')

        return {'publisher_form':None,
                'main':main}
    
    if 'slug' in request.matchdict:

        slug = request.matchdict.get('slug')
        session = request.rel_db_session
        publisher = session.query(rel_models.Publisher).filter_by(name_slug=slug).one()
        
        publisher_form['name'].widget = deform.widget.TextInputWidget(disabled="disabled")
        
        return {'publisher_form': publisher_form.render(publisher.as_dict(), ),
                'main':main}

    return {'publisher_form': publisher_form.render(),
            'main':main}


def new_book(request):
    main = get_renderer(BASE_TEMPLATE).implementation()
    evaluation_form = EvaluationForm.get_form()

    publishers = request.rel_db_session.query(rel_models.Publisher.name_slug, rel_models.Publisher.name).all()
    evaluation_form['publisher'].widget = deform.widget.SelectWidget(values=(publishers), )

    if 'submit' in request.POST:

        controls = request.POST.items()
        try:
            appstruct = evaluation_form.validate(controls)
        except deform.ValidationFailure, e:
            return {'monograph_form':e.render(), 'main':main}

        publisher_slug = appstruct.pop('publisher')
        publisher = request.rel_db_session.query(rel_models.Publisher).filter_by(name_slug=publisher_slug).one()
        evaluation = rel_models.Evaluation(**appstruct)

        evaluation.publisher = publisher

        request.rel_db_session.add(evaluation)
        try:
            request.rel_db_session.commit()
        except IntegrityError:
            request.rel_db_session.rollback()
            request.session.flash(u'Esse registro já existe.')
            return {'monograph_form':evaluation_form.render(appstruct), 'main':main}
        
        monograph = Monograph(title=evaluation.title, isbn=evaluation.isbn, publisher=evaluation.publisher.name)
        monograph.save(request.db)

        return HTTPFound(location=request.route_path('staff.edit_book', sbid=monograph._id))

    return {'monograph_form': evaluation_form.render(),
            'main':main}

