from pyramid.view import view_config
from pyramid.response import Response
from pyramid import exceptions
from pyramid.url import route_url, static_url
from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import get_renderer
from pyramid.i18n import TranslationStringFactory, negotiate_locale_name
_ = TranslationStringFactory('scielobooks')

from ..utilities.functions import create_thumbnail

import couchdbkit
import urllib2
import json
import deform
import Image
import StringIO
import os


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

def book_details(request):
    sbid = request.matchdict['sbid']
    try:
        document = request.db.get(sbid)
    except couchdbkit.ResourceNotFound:
        raise exceptions.NotFound()
    if document['TYPE'] != 'Monograph':
        raise exceptions.NotFound()

    if not document['visible']:
        raise exceptions.NotFound() #TODO change exception!

    isbn = document['isbn']

    document['chapters_list'] = [dict(chap) for chap in document['chapters_list']]
    document['creators'] = [dict(creator) for creator in document['creators']]

    for num,chapter in enumerate(document['chapters_list']):
        shortname = document['shortname']
        partnumber = str(num).zfill(2)

        pdf_url = static_url('scielobooks:books/%s/pdf/%s.pdf', request) % (sbid, partnumber)
        chapter['url'] = pdf_url
        chapter['preview_url'] = request.route_path(
            'catalog.chapter_details',sbid=sbid, chapter=partnumber)

    download_formats = []
    for format in document['download_formats']:
        if format in MIMETYPES:
            if format == 'application/pdf':
                pdf_url = static_url('scielobooks:books/%s/pdf/%s.pdf', request) % (sbid, isbn)
                download_formats.append(dict(name=MIMETYPES[format], url=pdf_url))
            else:
                download_formats.append(dict(name=MIMETYPES[format], url='#'))

    document.update({
        'download_formats': download_formats,
        'cover_url': request.route_path('catalog.cover', sbid=sbid, size='sz1'),
        'breadcrumb': {'home':request.registry.settings['solr_url'],},
        'creators': main_fields(document['creators']),
    })

    main = get_renderer(BASE_TEMPLATE).implementation()

    return {'document':document,
            'main':main}

def chapter_details(request):
    sbid = request.matchdict['sbid']
    try:
        chapter = int(request.matchdict['chapter'])
    except ValueError:
        raise exceptions.NotFound(_('Not a valid chapter'))

    try:
        document = request.db.get(sbid)#monographic sbid, not the analictic one!
    except couchdbkit.ResourceNotFound:
        raise exceptions.NotFound()
    isbn = document['isbn']
    if document['TYPE'] != 'Monograph':
        raise exceptions.NotFound()

    document['chapters_list'] = [dict(chap) for chap in document['chapters_list']]
    document['creators'] = [dict(creator) for creator in document['creators']]

    try:
        chapter_sbid = document['chapters_list'][chapter]['sbid']
    except IndexError:
        raise exceptions.NotFound(_('Not a valid chapter'))

    try:
        chapter_document = request.db.get(chapter_sbid)
    except couchdbkit.ResourceNotFound:
        raise exceptions.NotFound()

    for num,chapter in enumerate(document['chapters_list']):
        shortname = document['shortname']
        partnumber = str(num).zfill(2)
        chapter['preview_url'] = request.route_path('catalog.chapter_details',sbid=sbid, chapter=partnumber)

    partnumber = request.matchdict['chapter']
    partnumber.zfill(2)

    pdf_url = static_url('scielobooks:books/%s/pdf/%s.pdf', request) % (sbid, partnumber)

    chapter_document['creators'] = [dict(creator) for creator in chapter_document['creators']]

    creators = main_fields(chapter_document['creators']) if chapter_document['creators'] \
                            else main_fields(document['creators'])
    document.update({
        'creators': creators,
        'pdf_url': pdf_url,
        'chaptertitle': chapter_document['title'],
        'pages': chapter_document['pages'],
        'partnumber': partnumber,
        'cover_url': request.route_path('catalog.cover', sbid=sbid, size='sz1'),
    })

    document['breadcrumb'] = {'home':request.registry.settings['solr_url'],
                              'book':request.route_path('catalog.book_details',
                                                        sbid=sbid)
                              }

    main = get_renderer(BASE_TEMPLATE).implementation()

    return {'document':document,
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


