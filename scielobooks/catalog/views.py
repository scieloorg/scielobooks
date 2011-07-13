from pyramid.view import view_config
from pyramid.response import Response
from pyramid import exceptions
from pyramid.url import route_url, static_url
from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import get_renderer
from pyramid.i18n import TranslationStringFactory, negotiate_locale_name
_ = TranslationStringFactory('scielobooks')

from ..staff.models import Monograph, Part
from scielobooks.utilities import functions

import couchdbkit
import urllib2
import deform

BASE_TEMPLATE = 'scielobooks:templates/base.pt'
MIMETYPES = {
    'application/pdf':'PDF',
    'application/epub':'ePub',
}
COVER_SIZES = {
    # id:(width, height),
    'sz1':(160, 160),
    'sz2':(180, 180),
}

def main_fields(composite_property):
    if isinstance(composite_property, list):
        return [subfield['full_name'] for subfield in composite_property]
    else:
        return composite_property['full_name']

def get_book_parts(monograph_sbid, request):
    try:
       parts = request.db.view('scielobooks/monographs_and_parts', include_docs=True, key=[monograph_sbid, 1])
    except couchdbkit.ResourceNotFound:
        raise exceptions.NotFound()

    monograph_parts = []
    for i,part in enumerate(parts):
        partnumber = str(i).zfill(2)
        part_meta = {'part_sbid':part['id'],
                     'partnumber':partnumber,
                     'title':part['doc']['title'],                     
                     'pdf_url':request.route_path('catalog.pdf_file', sbid=monograph_sbid, part=partnumber),
                     'preview_url':request.route_path('catalog.chapter_details',sbid=monograph_sbid, chapter=partnumber),
                     'swf_url': request.route_path('catalog.swf_file', sbid=monograph_sbid, part=partnumber),
                     'edit_url':request.route_path('staff.edit_part', sbid=monograph_sbid, part_id=part['id']),
                     }
        monograph_parts.append(part_meta)
    
    return monograph_parts

def book_details(request):
    sbid = request.matchdict['sbid']
    try:
        monograph = Monograph.get(request.db, sbid)
    except couchdbkit.ResourceNotFound:
        raise exceptions.NotFound()
        
    if not monograph.visible:
        raise exceptions.NotFound()

    parts = get_book_parts(monograph._id, request)

    book_attachments = []
    if getattr(monograph, 'pdf_file', None):
        pdf_file_url = request.route_path('catalog.pdf_file', sbid=monograph._id, part=monograph.isbn)
        book_attachments.append({'url':pdf_file_url, 'text':_('Book in PDF')})

    main = get_renderer(BASE_TEMPLATE).implementation()
    
    return {'document':monograph,
            'book_attachments':book_attachments,
            'parts':parts,
            'cover_thumb_url': request.route_path('catalog.cover_thumbnail', sbid=monograph._id),
            'cover_full_url': request.route_path('catalog.cover', sbid=monograph._id),
            'breadcrumb': {'home':request.registry.settings['solr_url'],},
            'main':main}

def chapter_details(request):
    sbid = request.matchdict['sbid']
    try:
        chapter = int(request.matchdict['chapter'])
    except ValueError:
        raise exceptions.NotFound(_('Not a valid chapter'))

    try:
        monograph = Monograph.get(request.db, sbid)
    except couchdbkit.ResourceNotFound:
        raise exceptions.NotFound()
        
    if not monograph.visible:
        raise exceptions.NotFound()

    parts = get_book_parts(monograph._id, request)

    try:
        part = parts[chapter]
    except IndexError:
        raise exceptions.NotFound(_('Not a valid chapter'))

    main = get_renderer(BASE_TEMPLATE).implementation()

    return {'document':monograph,
            'document_pdf_url': request.route_path('catalog.pdf_file', sbid=monograph._id, part=monograph.isbn),
            'parts':parts,
            'part':part,            
            'cover_thumb_url': request.route_path('catalog.cover_thumbnail', sbid=monograph._id),
            'breadcrumb':{'home':request.registry.settings['solr_url'],
                          'book':request.route_path('catalog.book_details', sbid=sbid),},
            'main':main}

def cover(request):
    sbid = request.matchdict['sbid']

    try:
        monograph = request.db.get(sbid)
        if 'thumbnail' in request.path:
            img = request.db.fetch_attachment(monograph,monograph['cover_thumbnail']['filename'])
        else:
            img = request.db.fetch_attachment(monograph,monograph['cover']['filename'])
    except (couchdbkit.ResourceNotFound, KeyError):
        img = urllib2.urlopen(static_url('scielobooks:static/images/fakecover.jpg', request))

        return Response(body=img.read(), content_type='image/jpeg')

    return Response(body=img, content_type='image/jpeg')

def pdf_file(request):
    sbid = request.matchdict['sbid']
    req_part = request.matchdict['part']

    monograph = Monograph.get(request.db, sbid)
    if req_part == monograph.isbn:
        try:
            pdf_file = request.db.fetch_attachment(monograph._id, monograph.pdf_file['filename'])
        except (couchdbkit.ResourceNotFound, AttributeError):
            raise exceptions.NotFound()
    else:
        parts = get_book_parts(monograph._id, request)
        try:
            selected_part = parts[int(req_part)]
        except (IndexError, ValueError):            
            raise exceptions.NotFound()

        part = Part.get(request.db, selected_part['part_sbid'])
        try:
            pdf_file = request.db.fetch_attachment(part._id, part.pdf_file['filename'])
        except (couchdbkit.ResourceNotFound, AttributeError):
            raise exceptions.NotFound()

    return Response(body=pdf_file, content_type='application/pdf')

def swf_file(request):
    sbid = request.matchdict['sbid']
    req_part = request.matchdict['part']
    
    monograph = Monograph.get(request.db, sbid)
    if req_part == monograph.isbn:
        try:
            pdf_file = request.db.fetch_attachment(monograph._id, monograph.pdf_file['filename'])
        except (couchdbkit.ResourceNotFound, AttributeError):
            raise exceptions.NotFound()
    else:
        parts = get_book_parts(monograph._id, request)
        try:
            selected_part = parts[int(req_part)]
        except (IndexError, ValueError):            
            raise exceptions.NotFound()

        part = Part.get(request.db, selected_part['part_sbid'])
        try:
            pdf_file = request.db.fetch_attachment(part._id, part.pdf_file['filename'])
        except (couchdbkit.ResourceNotFound, AttributeError):
            raise exceptions.NotFound()

    swf_file = functions.convert_pdf2swf(pdf_file)

    return Response(body=swf_file.read(), content_type='application/x-shockwave-flash')