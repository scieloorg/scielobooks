#!/usr/bin/env python
# coding:utf-8
"""
Script that makes the inverse way of export-tools/dump_couchdb.py

"""


import couchdbkit
import os
import json
import sys
import ConfigParser

def load_doc(sbid):
    """
    Load a doc for a given sbid
    """
    data_path = os.path.join(base_dir, sbid, 'data.json')
    doc = json.loads(open(data_path).read())
    try:
        del(doc['_attachments'])
        del(doc['_rev'])
    except KeyError:
        # delete the item only if it exists
        pass
    return doc

def upload_attachments(doc):
    doc_data_path = os.path.join(base_dir, doc['_id'])
    for attach in ['pdf_file', 'epub_file', 'cover', 'toc', 'editorial_decision', 'cover_thumbnail']:

        if attach in doc:
            filename = doc[attach].get('filename', None)
            if filename is not None:
                f = open(os.path.join(doc_data_path, attach, filename), 'r')
                db.put_attachment(doc, f, filename)

def save_doc(sbid):
    doc = load_doc(sbid)
    db.save_doc(doc)
    upload_attachments(doc)


if __name__ == '__main__':

    try:
        config_file = sys.argv[1]
    except IndexError:
        sys.exit('Missing application config file')

    try:
        base_dir = sys.argv[2]
    except IndexError:
        sys.exit('Missing base dir')

    config = ConfigParser.ConfigParser()
    config.read(config_file)

    server = couchdbkit.Server(config.get('app:scielobooks', 'db_uri'))
    db = server[config.get('app:scielobooks', 'db_name')]

    for doc in os.listdir(base_dir):
        save_doc(doc)
