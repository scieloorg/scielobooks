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
import deform
import Image
import StringIO
import colander

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
        return [subfield['name'] for subfield in composite_property]
    else:
        return composite_property['name']

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
                                                      sbid=book['value']['monograph']),
                     }
        documents[book['key']].append(book_meta)

    main = get_renderer(BASE_TEMPLATE).implementation()

    return {'documents': documents,
            'total_documents': len(books),
            'main':main}

def cover(request):
    sbid = request.matchdict['sbid']
    size = request.matchdict['size']

    try:
        monograph = request.db.get(sbid)        
    except couchdbkit.ResourceNotFound:
        raise exceptions.NotFound()
    
    if monograph['TYPE'] != 'Monograph':
        raise exceptions.NotFound()

    try:
        attach_name = monograph['cover']['filename']
    except KeyError:
        raise exceptions.NotFound()

    if size in COVER_SIZES:
        img_size = COVER_SIZES[size]
    else:
        size = 'sz1'
        img_size = COVER_SIZES['sz1']

    filepath = '/tmp/cover-%s.%s.JPEG' % (monograph['_id'], size)
    
    cover_url = static_url('scielobooks:database/%s/%s', request) % (monograph['_id'], attach_name)
    
    try:
        img = urllib2.urlopen(cover_url.replace(' ', '%20'))#FIXME: urlencode must be handled more seriously
        img_thumb = Image.open(StringIO.StringIO(img.read()))
        img_thumb.thumbnail(img_size, Image.ANTIALIAS)
        img_thumb.save(filepath, 'JPEG')

        return Response(body=open(filepath).read(), content_type='image/jpeg')
    except urllib2.HTTPError:
        img = urllib2.urlopen(static_url('scielobooks:static/images/fakecover.jpg', request))

        return Response(body=img.read(), content_type='image/jpeg')