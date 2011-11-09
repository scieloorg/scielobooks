#!/usr/bin/env python
# coding: utf-8
import couchdbkit
import os
import json
import sys
import ConfigParser

class ConsistencyError(Exception):
    pass

def check_consistency(doc):
    for attr in ['title']:
        if attr not in doc:
            raise ConsistencyError

def ensure_dir_exists(dirname):
    if not os.path.exists(dirname):
        os.makedirs(dirname)

def get_entire_book(monograph_sbid):
    try:
        sbids = [doc['id'] for doc in db.view('scielobooks/monographs_and_parts',
            include_docs=False, startkey=[monograph_sbid, 0], endkey=[monograph_sbid, 1])]
    except couchdbkit.ResourceNotFound:
        raise exceptions.NotFound()

    return sbids

def monograph_list():
    try:
        sbids = [doc['id'] for doc in db.view('scielobooks/books', include_docs=False,)]
    except couchdbkit.ResourceNotFound:
        raise exceptions.NotFound()

    return sbids



if __name__ == '__main__':

    try:
        config_file = sys.argv[1]
    except IndexError:
        sys.exit('Missing application config file')

    config = ConfigParser.ConfigParser()
    config.read(config_file)

    server = couchdbkit.Server(config.get('app:scielobooks', 'db_uri'))
    db = server[config.get('app:scielobooks', 'db_name')]

    for book_sbid in monograph_list():
        for doc_sbid in get_entire_book(book_sbid):
            doc = db.get(doc_sbid)
            # try:
            #     check_consistency(doc)
            # except ConsistencyError:
            #     #add to a consistency log
            #     continue

            base_dir = 'attachs'
            document_files_dir = os.path.join(base_dir, doc['_id'])
            ensure_dir_exists(document_files_dir)

            with open(os.path.join(document_files_dir, 'data.json'), 'w') as f:
                del(doc['_rev'])
                f.write(json.dumps(doc))

            #download attachs
            for attach in ['pdf_file', 'epub_file', 'cover', 'toc', 'editorial_decision', 'cover_thumbnail']:
                if doc.get(attach):
                    filename = doc[attach].get('filename')
                    if filename:
                        destination_dir = os.path.join(document_files_dir, attach)
                        ensure_dir_exists(destination_dir)

                        with open(os.path.join(destination_dir, filename), 'w') as f:
                            f.write(db.fetch_attachment(doc['_id'], filename))





