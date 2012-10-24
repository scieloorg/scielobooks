# coding: utf-8
import couchdbkit
from pyramid import exceptions

from scielobooks.staff import models


def list_publishers(request):

    def _prepare_response(data):
        resp = {
            'total_items': data['value'],
            'title': data['key'],
            '_id': data['key'],
        }

        return resp

    try:
        publishers = [_prepare_response(pub) for pub in request.db.view('scielobooks/publishers', group=True)]
    except couchdbkit.ResourceNotFound:
        raise exceptions.NotFound()

    return publishers


def list_alphasum(request):

    def _prepare_response(data):
        resp = {
            'total_items': data['value'],
            'title': data['key'],
            '_id': data['key'],
        }

        return resp

    try:
        letters = [_prepare_response(letter) for letter in request.db.view('scielobooks/alphabetical', group=True)]
    except couchdbkit.ResourceNotFound:
        raise exceptions.NotFound()

    return letters


def list_books(request):

    def _prepare_response(data):
        book = models.Monograph(**data)

        if getattr(book, 'pdf_file', None):
            pdf_file_url = request.route_path(
                'catalog.pdf_file', sbid=book._id, part=book.shortname)
        else:
            pdf_file_url = ''

        if getattr(book, 'epub_file', None):
            epub_file_url = request.route_path(
                'catalog.epub_file', sbid=book._id, part=book.shortname)
        else:
            epub_file_url = ''

        if getattr(book, 'cover', None):
            cover_url = request.route_path('catalog.cover', sbid=book._id)
        else:
            cover_url = ''

        if getattr(book, 'cover_thumbnail', None):
            cover_thumb_url = request.route_path('catalog.cover_thumbnail', sbid=book._id)
        else:
            cover_thumb_url = ''

        resp = {
            'publisher': data.get('publisher', ''),
            '_id': data.get('_id', ''),
            'pisbn': data.get('isbn', ''),
            'eisbn': data.get('eisbn', ''),
            'language': data.get('language', ''),
            'updated': data.get('publication_date', ''),
            'pdf_file': {
                'type': 'application/pdf',
                'uri': pdf_file_url,
            },
            'epub_file': {
                'type': 'application/epub+zip',
                'uri': epub_file_url,
            },
            'cover_thumbnail': {
                'type': 'image/jpeg',
                'uri': cover_thumb_url,
            },
            'cover': {
                'type': 'image/jpeg',
                'uri': cover_url,
            },
            'synopsis': data.get('synopsis', ''),
            'year': data.get('year', ''),
            'title': data.get('title', ''),
            'creators': [{
                'name': '',
                'role': '',
                'link_resume': '',
            }],
        }
        return resp

    try:
        books = [_prepare_response(book['doc']) for book in request.db.view('scielobooks/books_by_alpha', include_docs=True)]
    except couchdbkit.ResourceNotFound:
        raise exceptions.NotFound()

    return books