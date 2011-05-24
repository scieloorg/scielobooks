#!/usr/bin/env python
# coding: utf-8

import json
from isbn import toISBN13, InvalidISBN
from base28 import reprbase

TABLE_HEADER = "||'''SBID'''||'''ISBN-13'''||'''ISBN dado'''||'''Título'''||'''Caminho no file system'''||"

with open('scielobooks.json') as jfile:
    jstruct = json.load(jfile)

print TABLE_HEADER

for book in (r for r in jstruct if r['98'][0] == 'FONTE'):
    title = book['18'][0].strip()
    title = title.split('^')[0]
    isbn = book['69'][0].strip()
    idnum = book['2'][0].strip()

    try:
        isbn13 = toISBN13(isbn)
    except InvalidISBN:
        isbn13 = '?'*13

    sbid = reprbase(int(idnum))

    print '||%s||%s||%s||%s|| ||' % (sbid, isbn13, isbn, title)

