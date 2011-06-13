# coding: utf-8

from pyramid.view import view_config
from pyramid.response import Response
from pyramid import exceptions
from pyramid.url import route_url, static_url
from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import get_renderer
from pyramid.i18n import TranslationStringFactory
_ = TranslationStringFactory('scielobooks')

from sqlalchemy.exc import IntegrityError
from datetime import date

from forms import MonographForm, PublisherForm, EvaluationForm, MeetingForm
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

from .models import Monograph, Part
from ..utilities.functions import create_thumbnail

BASE_TEMPLATE = 'scielobooks:templates/base.pt'
MIMETYPES = {
    'application/pdf':'pdf',
    'application/epub':'epub',
}

def edit_book(request):
    FORM_TITLE = 'Submission of %s'

    monograph_form = MonographForm.get_form()

    main = get_renderer(BASE_TEMPLATE).implementation()

    if 'submit' in request.POST:
   
        controls = request.POST.items()
        try:
            appstruct = monograph_form.validate(controls)
        except deform.ValidationFailure, e:
            
            return {'content':e.render(), 
                    'main':main, 
                    'form_title':FORM_TITLE % monograph.title,
                    }
        
        if appstruct['cover'] and appstruct['cover']['fp'] is not None:
            cover_thumbnail = {'fp': create_thumbnail(appstruct['cover']['fp']),
                               'filename': appstruct['cover']['filename'] + '.thumb.jpeg',
                               'uid':'', 
                               }
            appstruct['cover_thumbnail'] = cover_thumbnail
        
        monograph = Monograph.from_python(appstruct)
        monograph.save(request.db)

        request.session.flash('Atualizado com sucesso.')

        return HTTPFound(location=request.route_path('staff.book_details', sbid=monograph._id))
    
    if 'sbid' in request.matchdict:        
        monograph = Monograph.get(request.db, request.matchdict['sbid'])
        appstruct = monograph.to_python()

        return {'content':monograph_form.render(appstruct),
                'main':main,
                'form_title':FORM_TITLE % monograph.title,
                }
    
    raise exceptions.NotFound

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
                     'edit_url':request.route_path('staff.edit_part', sbid=monograph_id, part_id=part['id']),
                     }

        documents[part['id']] = part_meta    
    
    main = get_renderer(BASE_TEMPLATE).implementation()

    return {'documents': documents,
            'main':main,
            }

def new_part(request):
    FORM_TITLE_NEW = 'New Book Part'
    FORM_TITLE_EDIT = 'Editing %s'

    monograph_id = request.matchdict['sbid']

    part_schema = Part.get_schema()
    part_form = deform.Form(part_schema, buttons=('submit',))

    main = get_renderer(BASE_TEMPLATE).implementation()

    if 'submit' in request.POST:
   
        controls = request.POST.items()
        try:
            appstruct = part_form.validate(controls)
        except deform.ValidationFailure, e:
            return {'content':e.render(),
                    'main':main,
                    'form_title':FORM_TITLE_NEW,
                    }
                
        part = Part.from_python(appstruct)
        part.monograph = monograph_id

        part.save(request.db)
        request.session.flash('Adicionado com sucesso.')
    
        return HTTPFound(location=request.route_path('staff.panel'))

    if 'part_id' in request.matchdict:
        part = Part.get(request.db, request.matchdict['part_id'])
        
        return {'content':part_form.render(part.to_python()),
                'main':main,
                'form_title':FORM_TITLE_EDIT % part.title,
                }

    return {'content':part_form.render(),
            'main':main,
            'form_title':FORM_TITLE_NEW,
            }

def book_details(request):
    main = get_renderer(BASE_TEMPLATE).implementation()
    
    sbid = request.matchdict['sbid']
    try:
        monograph = request.db.get(sbid)
    except couchdbkit.ResourceNotFound:
        raise exceptions.NotFound()
    if monograph['TYPE'] != 'Monograph': #FIXME! Really necessary?
        raise exceptions.NotFound()

    creators = [dict(creator)['full_name'] for creator in monograph['creators']]
    
    document = monograph
    
    document.update({
        'cover_thumb': request.route_path('catalog.cover_thumbnail', sbid=sbid),
        'cover_full': request.route_path('catalog.cover', sbid=sbid),
        'breadcrumb': {'home':request.registry.settings['solr_url'],},
        'creators': creators,
    })

    return {'document':document,
            'main':main,
            }


def panel(request):
    evaluations = request.rel_db_session.query(rel_models.Evaluation).all()
    meetings = request.rel_db_session.query(rel_models.Meeting).all()

    main = get_renderer(BASE_TEMPLATE).implementation()

    return {'evaluations': evaluations,
            'meetings': meetings,
            'main':main,
            }

def new_publisher(request):
    FORM_TITLE_NEW = 'New Publisher'
    FORM_TITLE_EDIT = 'Editing %s'

    main = get_renderer(BASE_TEMPLATE).implementation()
    
    publisher_form = PublisherForm.get_form()
    
    if 'submit' in request.POST:

        controls = request.POST.items()
        try:
            appstruct = publisher_form.validate(controls)
        except deform.ValidationFailure, e:
            return {'content':e.render(),
                    'main':main,
                    'form_title':FORM_TITLE_NEW,
                    }
    
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
            return {'content':publisher_form.render(appstruct),
                    'main':main,
                    'form_title':FORM_TITLE_NEW,
                    }

        request.session.flash('Adicionado com sucesso.')

        return HTTPFound(location=request.route_path('staff.panel'))
    
    if 'slug' in request.matchdict:

        slug = request.matchdict.get('slug')
        session = request.rel_db_session
        publisher = session.query(rel_models.Publisher).filter_by(name_slug=slug).one()
        
        publisher_form['name'].widget = deform.widget.TextInputWidget(disabled="disabled")
        
        return {'content': publisher_form.render(publisher.as_dict()),
                'main':main,
                'form_title':FORM_TITLE_EDIT % publisher.name,
                }

    return {'content': publisher_form.render(),
            'main':main,
            'form_title':FORM_TITLE_NEW,
            }


def new_book(request):
    FORM_TITLE_NEW = 'New Book Submission'

    main = get_renderer(BASE_TEMPLATE).implementation()
    evaluation_form = EvaluationForm.get_form()

    publishers = request.rel_db_session.query(rel_models.Publisher.name_slug, rel_models.Publisher.name).all()
    evaluation_form['publisher'].widget = deform.widget.SelectWidget(values=(publishers), )

    if 'submit' in request.POST:

        controls = request.POST.items()
        try:
            appstruct = evaluation_form.validate(controls)
        except deform.ValidationFailure, e:
            return {'content':e.render(),
                    'main':main,
                    'form_title':FORM_TITLE_NEW,
                    }

        publisher_slug = appstruct.pop('publisher')
        publisher = request.rel_db_session.query(rel_models.Publisher).filter_by(name_slug=publisher_slug).one()
        evaluation = rel_models.Evaluation(**appstruct)

        evaluation.publisher = publisher

        monograph = Monograph(title=evaluation.title, 
                              isbn=evaluation.isbn, 
                              publisher=evaluation.publisher.name,
                              )
        
        evaluation.monograph_sbid = monograph._id
                              
        request.rel_db_session.add(evaluation)
        try:
            request.rel_db_session.commit()
        except IntegrityError:
            request.rel_db_session.rollback()
            request.session.flash(u'Esse registro já existe.')
            return {'content':evaluation_form.render(appstruct),
                    'main':main,
                    'form_title':FORM_TITLE_NEW,
                    }
        
        monograph.save(request.db)

        return HTTPFound(location=request.route_path('staff.edit_book', sbid=monograph._id))

    return {'content': evaluation_form.render(),
            'main':main,
            'form_title':FORM_TITLE_NEW,
            }

def new_meeting(request):
    FORM_TITLE_NEW = 'New Meeting'

    main = get_renderer(BASE_TEMPLATE).implementation()

    meeting_form = MeetingForm.get_form()

    if 'submit' in request.POST:
        
        controls = request.POST.items()
        try:
            appstruct = meeting_form.validate(controls)
        except deform.ValidationFailure, e:
            return {'content':e.render(),
                    'main':main,
                    'form_title':FORM_TITLE_NEW,
                    }
    
        meeting = rel_models.Meeting(**appstruct)

        request.rel_db_session.add(meeting)
        #TODO! catch exception
        request.rel_db_session.commit()
    
        return HTTPFound(location=request.route_path('staff.panel'))

    return {'content':meeting_form.render({'date':date.today()}),
            'main':main,
            'form_title':FORM_TITLE_NEW,
            }


def ajax_set_meeting(request):
    if request.method == 'POST':        
        evaluation_isbn = request.POST.get('evaluation', None)
        meeting_id = request.POST.get('meeting', None)

        if evaluation_isbn is None or meeting_id is None:
            return Respose('insufficient params')
        
        #TODO! catch exception
        evaluation = request.rel_db_session.query(rel_models.Evaluation).filter_by(isbn=evaluation_isbn).one()
        meeting = request.rel_db_session.query(rel_models.Meeting).filter_by(id=meeting_id).one()

        evaluation.meeting = meeting
        request.rel_db_session.add(evaluation)
        #TODO! catch exception
        request.rel_db_session.commit()

        return Response('done')

    return Response('nothing to do')