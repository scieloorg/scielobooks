# coding: utf-8

from pyramid.view import view_config
from pyramid.response import Response
from pyramid import exceptions
from pyramid.url import route_url, static_url
from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import get_renderer
from pyramid.security import authenticated_userid
from pyramid.i18n import get_localizer
from pyramid.i18n import TranslationStringFactory
_ = TranslationStringFactory('scielobooks')

from sqlalchemy.exc import IntegrityError
from datetime import date

from forms import MonographForm, PublisherForm, EvaluationForm, MeetingForm
from ..models import models as rel_models
from ..users import models as user_models
from ..catalog import views as catalog_views

import couchdbkit
import deform
import colander
import urllib

from .models import Monograph, Part
from ..utilities.functions import create_thumbnail

BASE_TEMPLATE = 'scielobooks:templates/base.pt'
MIMETYPES = {
    'application/pdf':'pdf',
    'application/epub':'epub',
}
STATUS_CHOICES = {'under-evaluation': _('Under Evaluation'),
                  'accepted': _('Accepted'),
                  'accepted-with-condition': _('Accepted with Condition'),
                  'rejected': _('Rejected'),
                  }

class Catalog(object):
    """
    Represents a paginated set of evaluation records
    """
    def __init__(self, queryset, limit=10):
        self._queryset = queryset
        self._limit = int(limit)
        self.total_items = self._queryset.count()

    def page(self, page_number):
        offset = (page_number - 1) * self._limit
        return self._queryset.limit(self._limit).offset(offset).all()

    @property
    def total_pages(self):
        return (self.total_items + self._limit // 2) // self._limit

def get_logged_user(request):
    userid = authenticated_userid(request)
    if userid:
        return request.rel_db_session.query(user_models.User).get(userid)

def edit_book(request):
    FORM_TITLE = _('Submission of %s')

    localizer = get_localizer(request)
    monograph_form = MonographForm.get_form(localizer)

    main = get_renderer(BASE_TEMPLATE).implementation()

    if request.method == 'POST':
        if 'btn_cancel' in request.POST:
            return HTTPFound(location=request.route_url('staff.book_details', sbid=request.matchdict['sbid']))

        controls = request.POST.items()
        try:
            appstruct = monograph_form.validate(controls)
        except deform.ValidationFailure, e:

            monograph = Monograph.get(request.db, request.matchdict['sbid'])
            return {'content':e.render(),
                    'main':main,
                    'user':get_logged_user(request),
                    'general_stuff':{'form_title':FORM_TITLE % monograph.title,
                              'breadcrumb': [
                                (_('Dashboard'), request.route_url('staff.panel')),
                                (monograph.title, request.route_url('staff.book_details', sbid=monograph._id)),
                                (_('Edit'), None),
                              ]
                             },
                    }

        if appstruct['cover'] and appstruct['cover']['fp'] is not None:
            cover_thumbnail = {'fp': create_thumbnail(appstruct['cover']['fp']),
                               'filename': appstruct['cover']['filename'] + '.thumb.jpeg',
                               'uid':'',
                               }
            appstruct['cover_thumbnail'] = cover_thumbnail

        existing_doc_appstruct = Monograph.get(request.db, appstruct['_id']).to_python()
        existing_doc_appstruct.update(appstruct)
        monograph = Monograph.from_python(existing_doc_appstruct)
        monograph.save(request.db)

        request.session.flash(_('Successfully updated.'))

        return HTTPFound(location=request.route_url('staff.book_details', sbid=monograph._id))

    if 'sbid' in request.matchdict:
        monograph = Monograph.get(request.db, request.matchdict['sbid'])
        appstruct = monograph.to_python()

        return {'content':monograph_form.render(appstruct),
                'main':main,
                'user':get_logged_user(request),
                'general_stuff':{'form_title':FORM_TITLE % monograph.title,
                              'breadcrumb': [
                                (_('Dashboard'), request.route_url('staff.panel')),
                                (monograph.title, request.route_url('staff.book_details', sbid=monograph._id)),
                                (_('Edit'), None),
                              ]
                             },
                }

    raise exceptions.NotFound

def parts_list(request):
    monograph_id = request.matchdict['sbid']
    try:
       parts = request.db.view('scielobooks/monographs_and_parts', include_docs=True, key=[monograph_id, 1])
    except couchdbkit.ResourceNotFound:
        raise exceptions.NotFound()

    documents = []
    for part in parts:
        part_meta = {'id':part['id'],
                     'title':part['doc']['title'],
                     'order':part['doc']['order'],
                     'creators':part['doc']['creators'],
                     'pdf_url':request.route_url('catalog.pdf_file', sbid=monograph_id, part=part['doc']['order']),
                     'edit_url':request.route_url('staff.edit_part', sbid=monograph_id, part_id=part['id']),
                     }

        documents.append(part_meta)

    main = get_renderer(BASE_TEMPLATE).implementation()

    return {'documents': documents,
            'main':main,
            'user':get_logged_user(request),
            }

def new_part(request):
    FORM_TITLE_NEW = _('New Book Part')
    FORM_TITLE_EDIT = _('Editing %s')

    monograph_id = request.matchdict['sbid']

    part_schema = Part.get_schema()
    part_form = deform.Form(part_schema, buttons=('submit',))

    main = get_renderer(BASE_TEMPLATE).implementation()

    if request.method == 'POST':

        controls = request.POST.items()
        try:
            appstruct = part_form.validate(controls)
        except deform.ValidationFailure, e:
            return {'content':e.render(),
                    'main':main,
                    'user':get_logged_user(request),
                    'general_stuff':{'form_title':FORM_TITLE_NEW},
                    }

        part = Part.from_python(appstruct)
        part.monograph = monograph_id

        is_new = True if getattr(part, '_rev', None) is None else False

        part.save(request.db)
        if is_new:
            request.session.flash(_('Successfully added.'))
        else:
            request.session.flash(_('Successfully updated.'))

        return HTTPFound(location=request.route_url('staff.edit_part', sbid=part.monograph, part_id=part._id))

    if 'part_id' in request.matchdict:
        part = Part.get(request.db, request.matchdict['part_id'])

        return {'content':part_form.render(part.to_python()),
                'main':main,
                'user':get_logged_user(request),
                'general_stuff':{'form_title':FORM_TITLE_EDIT % part.title},
                }

    return {'content':part_form.render(),
            'main':main,
            'user':get_logged_user(request),
            'general_stuff':{'form_title':FORM_TITLE_NEW},
            }

def book_details(request):
    main = get_renderer(BASE_TEMPLATE).implementation()

    sbid = request.matchdict['sbid']
    try:
        monograph = Monograph.get(request.db, sbid)
    except couchdbkit.ResourceNotFound:
        raise exceptions.NotFound()

    book_attachments = []
    if getattr(monograph, 'toc', None):
        toc_url = static_url('scielobooks:database/%s/%s', request) % (monograph._id, monograph.toc['filename'])
        book_attachments.append({'url':toc_url, 'text':_('Table of Contents')})

    if getattr(monograph, 'editorial_decision', None):
        editorial_decision_url = static_url('scielobooks:database/%s/%s', request) % (monograph._id, monograph.editorial_decision['filename'])
        book_attachments.append({'url':editorial_decision_url, 'text':_('Parecer da Editora')})

    if getattr(monograph, 'pdf_file', None):
        pdf_file_url = static_url('scielobooks:database/%s/%s', request) % (monograph._id, monograph.pdf_file['filename'])
        book_attachments.append({'url':pdf_file_url, 'text':_('Book in PDF')})

    evaluation = request.rel_db_session.query(rel_models.Evaluation).filter_by(monograph_sbid=monograph._id).one()

    parts = catalog_views.get_book_parts(monograph._id, request)

    return {'document':monograph,
            'document_parts':parts,
            'evaluation':evaluation,
            'book_attachments':book_attachments,
            'main':main,
            'user':get_logged_user(request),
            'cover_full_url': request.route_url('catalog.cover', sbid=monograph._id),
            'cover_thumb_url': request.route_url('catalog.cover_thumbnail', sbid=monograph._id),
            'add_part_url': request.route_url('staff.new_part', sbid=monograph._id),
            'general_stuff': {'breadcrumb': [
                                (_('Dashboard'), request.route_url('staff.panel')),
                                (monograph.title, None),
                              ]
                          }
            }

def panel(request):
    filter_publisher = request.params.get('publ', None)
    filter_meeting = request.params.get('meet', None)
    filter_committee_decision = request.params.get('cdec', None)
    filter_status = request.params.get('ispub', None)

    try:
        page = int(request.params.get('page', 1))
    except ValueError:
        page = 1

    evaluations = request.rel_db_session.query(rel_models.Evaluation)
    if filter_publisher is not None and len(filter_publisher) > 0:
        evaluations = evaluations.join(rel_models.Publisher).filter(rel_models.Publisher.name_slug==filter_publisher)
    if filter_meeting is not None and len(filter_meeting) > 0:
        evaluations = evaluations.join(rel_models.Meeting).filter(rel_models.Meeting.date==filter_meeting)
    if filter_committee_decision is not None and len(filter_committee_decision) > 0:
        evaluations = evaluations.filter(rel_models.Evaluation.status==filter_committee_decision)
    if filter_status is not None and len(filter_status) > 0:
        evaluations = evaluations.filter(rel_models.Evaluation.is_published==filter_status)

    filters = {'publ':filter_publisher if filter_publisher is not None else '',
               'meet':filter_meeting if filter_meeting is not None else '',
               'cdec':filter_committee_decision if filter_committee_decision is not None else '',
               'ispub':filter_status if filter_status is not None else '',
    }

    catalog = Catalog(evaluations, limit=request.registry.settings['pagination.items_per_page'])

    pagination_filters = dict([k, v] for k, v in filters.items() if v != '')
    pagination = []
    for k in range(catalog.total_pages):
        querystring_params = pagination_filters.copy()
        querystring_params['page'] = k+1
        pagination.append({'pg_number':k+1, 'url':urllib.urlencode(querystring_params)})

    meetings = request.rel_db_session.query(rel_models.Meeting).all()
    publishers = request.rel_db_session.query(rel_models.Publisher).all()

    main = get_renderer(BASE_TEMPLATE).implementation()

    committee_decisions = [{'text':label,'value':k} for k, label in STATUS_CHOICES.items()]

    return {'evaluations': catalog.page(page),
            'evaluations_total': catalog.total_items,
            'page':page,
            'pagination': pagination,
            'meetings': meetings,
            'publishers':publishers,
            'committee_decisions':committee_decisions,
            'main':main,
            'user':get_logged_user(request),
            'filters': filters,
            }

def new_publisher(request):
    FORM_TITLE_NEW = _('New Publisher')
    FORM_TITLE_EDIT = _('Editing %s')

    main = get_renderer(BASE_TEMPLATE).implementation()

    localizer = get_localizer(request)
    publisher_form = PublisherForm.get_form(localizer)

    if request.method == 'POST':
        if 'btn_cancel' in request.POST:
            return HTTPFound(location=request.route_url('staff.publishers_list'))

        controls = request.POST.items()
        try:
            appstruct = publisher_form.validate(controls)
        except deform.ValidationFailure, e:
            return {'content':e.render(),
                    'main':main,
                    'user':get_logged_user(request),
                    'general_stuff':{'form_title':FORM_TITLE_NEW,
                                  'breadcrumb': [
                                    (_('Dashboard'), request.route_url('staff.panel')),
                                    (_('Manage Publishers'), request.route_url('staff.publishers_list')),
                                    (_('New Publisher'), None),
                                  ]
                                },
                    }
        del(appstruct['__LOCALE__'])
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
            request.session.flash(_('This record already exists! Please check the data and try again.'))
            return {'content':publisher_form.render(appstruct),
                    'main':main,
                    'user':get_logged_user(request),
                    'general_stuff':{'form_title':FORM_TITLE_NEW,
                                  'breadcrumb': [
                                    (_('Dashboard'), request.route_url('staff.panel')),
                                    (_('Manage Publishers'), request.route_url('staff.publishers_list')),
                                    (_('New Publisher'), None),
                                  ]
                                 },
                    }

        request.session.flash(_('Successfully added.'))

        return HTTPFound(location=request.route_url('staff.publishers_list'))

    if 'slug' in request.matchdict:

        slug = request.matchdict.get('slug')
        session = request.rel_db_session
        publisher = session.query(rel_models.Publisher).filter_by(name_slug=slug).one()

        publisher_form['name'].widget = deform.widget.TextInputWidget(disabled="disabled")

        return {'content': publisher_form.render(publisher.as_dict()),
                'main':main,
                'user':get_logged_user(request),
                'general_stuff':{'form_title':FORM_TITLE_EDIT % publisher.name,
                              'breadcrumb': [
                                (_('Dashboard'), request.route_url('staff.panel')),
                                (_('Manage Publishers'), request.route_url('staff.publishers_list')),
                                (FORM_TITLE_EDIT % publisher.name, None),
                              ]
                            },
                }

    return {'content': publisher_form.render(),
            'main':main,
            'user':get_logged_user(request),
            'general_stuff':{'form_title':FORM_TITLE_NEW,
                          'breadcrumb': [
                            (_('Dashboard'), request.route_url('staff.panel')),
                            (_('Manage Publishers'), request.route_url('staff.publishers_list')),
                            (_('New Publisher'), None),
                          ]
                        },
            }

def publishers_list(request):
    main = get_renderer(BASE_TEMPLATE).implementation()
    publishers = request.rel_db_session.query(rel_models.Publisher).all()

    return {'publishers':publishers,
            'main':main,
            'user':get_logged_user(request),
            'general_stuff':{'breadcrumb': [
                            (_('Dashboard'), request.route_url('staff.panel')),
                            (_('Manage Publishers'), None),
                          ]
                         },
            }


def new_book(request):
    FORM_TITLE_NEW = _('New Book Submission')

    main = get_renderer(BASE_TEMPLATE).implementation()

    localizer = get_localizer(request)
    evaluation_form = EvaluationForm.get_form(localizer)

    publishers = request.rel_db_session.query(rel_models.Publisher.name_slug, rel_models.Publisher.name).all()
    evaluation_form['publisher'].widget = deform.widget.SelectWidget(values=(publishers), )

    if request.method == 'POST':
        if 'btn_cancel' in request.POST:
            return HTTPFound(location=request.route_url('staff.panel'))

        controls = request.POST.items()
        try:
            appstruct = evaluation_form.validate(controls)
        except deform.ValidationFailure, e:
            return {'content':e.render(),
                    'main':main,
                    'user':get_logged_user(request),
                    'general_stuff':{'form_title':FORM_TITLE_NEW},
                    }

        del(appstruct['__LOCALE__'])
        publisher_slug = appstruct.pop('publisher')
        publisher = request.rel_db_session.query(rel_models.Publisher).filter_by(name_slug=publisher_slug).one()
        appstruct['status'] = 'under-evaluation'
        evaluation = rel_models.Evaluation(**appstruct)

        evaluation.publisher = publisher

        monograph = Monograph(title=evaluation.title,
                              isbn=evaluation.isbn,
                              publisher=evaluation.publisher.name,
                              publisher_url=evaluation.publisher_catalog_url,
                              visible=False,
                              )

        evaluation.monograph_sbid = monograph._id
        request.rel_db_session.add(evaluation)
        try:
            request.rel_db_session.commit()
        except IntegrityError:
            request.rel_db_session.rollback()
            request.session.flash(_('This record already exists! Please check the data and try again.'))
            return {'content':evaluation_form.render(appstruct),
                    'main':main,
                    'user':get_logged_user(request),
                    'general_stuff':{'form_title':FORM_TITLE_NEW},
                    }

        monograph.save(request.db)

        return HTTPFound(location=request.route_url('staff.edit_book', sbid=monograph._id))

    return {'content': evaluation_form.render(),
            'main':main,
            'user':get_logged_user(request),
            'general_stuff':{'form_title':FORM_TITLE_NEW,
                          'breadcrumb': [
                            (_('Dashboard'), request.route_url('staff.panel')),
                            (_('New Submission'), None),
                          ]
                         },
            }

def delete_book(request):
    monograph_sbid = request.matchdict.get('sbid', None)

    if monograph_sbid is None:
        return Respose(status=204)

    #TODO! catch exception
    evaluation = request.rel_db_session.query(rel_models.Evaluation).filter_by(monograph_sbid=monograph_sbid).one()

    try:
        parts = [part['doc'] for part in request.db.view('scielobooks/monographs_and_parts',
            include_docs=True, startkey=[evaluation.monograph_sbid, 0], endkey=[evaluation.monograph_sbid, 1])]
    except couchdbkit.ResourceNotFound:
        raise exceptions.NotFound()

    request.rel_db_session.delete(evaluation)

    try:
        request.rel_db_session.commit()
        request.db.delete_docs(parts, all_or_nothing=True)
        request.session.flash(_('Successfully deleted.'))
    except:
        request.rel_db_session.rollback()

    return Response(status=200)

def new_meeting(request):
    FORM_TITLE_NEW = _('New Meeting')
    FORM_TITLE_EDIT = _('Editing %s')

    main = get_renderer(BASE_TEMPLATE).implementation()

    localizer = get_localizer(request)
    meeting_form = MeetingForm.get_form(localizer)

    if request.method == 'POST':
        if 'btn_cancel' in request.POST:
            return HTTPFound(location=request.route_url('staff.meetings_list'))

        controls = request.POST.items()
        try:
            appstruct = meeting_form.validate(controls)
        except deform.ValidationFailure, e:
            return {'content':e.render(),
                    'main':main,
                    'user':get_logged_user(request),
                    'general_stuff':{'form_title':FORM_TITLE_NEW,
                                  'breadcrumb': [
                                    (_('Dashboard'), request.route_url('staff.panel')),
                                    (_('Manage Meetings'), request.route_url('staff.meetings_list')),
                                    (_('New Meeting'), None),
                                  ]
                                 },
                                }

        del(appstruct['__LOCALE__'])
        appstruct['admin'] = get_logged_user(request)

        if 'id' in request.matchdict:
            meeting = request.rel_db_session.query(rel_models.Meeting).filter_by(id=request.matchdict['id']).one()
            meeting.date = appstruct['date']
            meeting.description = appstruct['description']

            request.session.flash(_('Successfully updated.'))
        else:
            meeting = rel_models.Meeting(**appstruct)
            request.session.flash(_('Successfully added.'))

        request.rel_db_session.add(meeting)
        #TODO! catch exception
        request.rel_db_session.commit()

        return HTTPFound(location=request.route_url('staff.meetings_list'))

    if 'id' in request.matchdict:
        meeting = request.rel_db_session.query(rel_models.Meeting).filter_by(id=request.matchdict['id']).one()
        appstruct = {'date':meeting.date, 'description':meeting.description}

        return {'content':meeting_form.render(appstruct),
                'main':main,
                'user':get_logged_user(request),
                'general_stuff':{'form_title':FORM_TITLE_EDIT % unicode(meeting.description),
                              'breadcrumb': [
                                (_('Dashboard'), request.route_url('staff.panel')),
                                (_('Manage Meetings'), request.route_url('staff.meetings_list')),
                                (FORM_TITLE_EDIT % unicode(meeting.description), None),
                              ]
                             },
                }

    return {'content':meeting_form.render({'date':date.today()}),
            'main':main,
            'user':get_logged_user(request),
            'general_stuff':{'form_title':FORM_TITLE_NEW,
                          'breadcrumb': [
                            (_('Dashboard'), request.route_url('staff.panel')),
                            (_('Manage Meetings'), request.route_url('staff.meetings_list')),
                            (_('New Meeting'), None),
                          ]
                         },
            }

def meetings_list(request):
    main = get_renderer(BASE_TEMPLATE).implementation()
    meetings = request.rel_db_session.query(rel_models.Meeting).all()

    return {'meetings':meetings,
            'main':main,
            'user':get_logged_user(request),
            'general_stuff':{'breadcrumb': [
                            (_('Dashboard'), request.route_url('staff.panel')),
                            (_('Manage Meetings'), None),
                          ]
                         },
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

def ajax_set_committee_decision(request):
    if request.method == 'POST':
        evaluation_isbn = request.POST.get('evaluation', None)
        decision = request.POST.get('decision', None)

        if evaluation_isbn is None or decision is None:
            return Respose('insufficient params')

        if decision not in STATUS_CHOICES:
            return Respose('invalid params')

        #TODO! catch exception
        evaluation = request.rel_db_session.query(rel_models.Evaluation).filter_by(isbn=evaluation_isbn).one()

        evaluation.status = decision
        request.rel_db_session.add(evaluation)
        #TODO! catch exception
        request.rel_db_session.commit()

        return Response('done')

    return Response('nothing to do')

def ajax_action_publish(request):
    if request.method == 'POST':
        evaluation_isbn = request.POST.get('evaluation', None)

        if evaluation_isbn is None:
            return Respose('insufficient params')

        #TODO! catch exception
        evaluation = request.rel_db_session.query(rel_models.Evaluation).filter_by(isbn=evaluation_isbn).one()

        if evaluation.status != 'accepted' and evaluation.status != 'accepted-with-condition':
            return Response('invalid action')

        if evaluation.is_published:
            return Response('nothing to do')

        monograph = Monograph.get(request.db, evaluation.monograph_sbid)

        evaluation.is_published = True
        monograph.visible = True

        request.rel_db_session.add(evaluation)
        monograph.save(request.db)

        #TODO! catch exception
        try:
            request.rel_db_session.commit()
        except:
            request.rel_db_session.rollback()
            monograph.visible = False
            monograph.save(request.db)

        return Response('done')

    return Response('nothing to do')

def ajax_action_unpublish(request):
    if request.method == 'POST':
        evaluation_isbn = request.POST.get('evaluation', None)

        if evaluation_isbn is None:
            return Respose('insufficient params')

        #TODO! catch exception
        evaluation = request.rel_db_session.query(rel_models.Evaluation).filter_by(isbn=evaluation_isbn).one()

        if not evaluation.is_published:
            return Response('nothing to do')

        monograph = Monograph.get(request.db, evaluation.monograph_sbid)

        evaluation.is_published = False
        monograph.visible = False

        request.rel_db_session.add(evaluation)
        monograph.save(request.db)

        #TODO! catch exception
        try:
            request.rel_db_session.commit()
        except:
            request.rel_db_session.rollback()
            monograph.visible = True
            monograph.save(request.db)

        return Response('done')

    return Response('nothing to do')

def ajax_action_delete_part(request):
    if request.method == 'POST':
        part_sbid = request.POST.get('part', None)

        if part_sbid is None:
            return Respose('insufficient params')

        request.db.delete_doc(part_sbid)
        request.session.flash(_('Successfully deleted.'))

        return Response('done')

    return Response('nothing to do')