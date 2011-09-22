#!/usr/bin/env python
# coding: utf-8

from scielobooks.utilities.isbn import toISBN13, InvalidISBN
from scielobooks.utilities.base28 import reprbase
from scielobooks.utilities.functions import create_thumbnail
from sys import argv
from scielobooks.staff import models
import unicodedata
import json
import couchdbkit
import urllib2
import os

db_name = 'scielobooks_1a'
db_uri = 'http://127.0.0.1:5984'

LILACS_IDNUM = "2"
LILACS_ISBN = "69"
LILACS_CHAPTER_ORDER = "902"
LILACS_CHAPER_NAME = "12"
LILACS_NIVEL_TRATAMENTO = "6"
LILACS_EDITORA = "62"
LILACS_RESUMO = "83"
LILACS_DATA_PUBLICACAO = "64"
LILACS_AUTOR_PESSOAL_MONOGRAFICO = "16"
LILACS_TITULO_ANALITICO = "12"
LILACS_TITULO_MONOGRAFICO = "18"
LILACS_PAGINAS_ANALITICO = "14"
LILACS_PAGINAS_MONOGRAFICO = "20"
LILACS_SBID_MONOGRAFICA = "903" #sbid da  monográfica ao qual a analítica pertence
LILACS_EDICAO = "63"
LILACS_ORDEM_CAPITULO = "902"
LILACS_AUTOR_PESSOAL_ANALITICO = "10"
LILACS_AUTOR_PESSOAL_MONOGRAFICO = "16"
LILACS_AUTOR_INSTITUCIONAL_ANALITICO = "11"
LILACS_AUTOR_INSTITUCIONAL_MONOGRAFICO = "17"
LILACS_LANGUAGE = "40"


def get(record, tag, missing=None):
    '''
    returns main subfield of first occurrence of tag in record, if found;
    otherwise returns missing value.
    '''
    return record[tag][0]['_'] if tag in record else missing


def create_chapters_lists(jstruct):
    lista_capitulos = {}    # {'isbn13':['nome_cap01', ...]}
    for analitica in (analitica for analitica in jstruct['docs']
                      if 'a' in analitica[LILACS_NIVEL_TRATAMENTO][0]['_']):
        try:
            isbn13 = str(toISBN13(get(analitica, LILACS_ISBN, '')))
        except (InvalidISBN, KeyError):
            isbn = get(analitica, LILACS_ISBN, 'faltante')
            isbns_invalidos.append((get(analitica, LILACS_IDNUM), isbn))
            continue

        ordem = int(get(analitica, LILACS_CHAPTER_ORDER, 999))
        sbid_analitica = reprbase(int(get(analitica, LILACS_IDNUM)))
        title_chapter = get(analitica, LILACS_CHAPER_NAME)
        titulo = [('title',title_chapter), ('sbid',sbid_analitica)]
        capitulo = (ordem, titulo)
        if lista_capitulos.has_key(isbn13):
            lista_capitulos[isbn13].append(capitulo)
        else:
            lista_capitulos[isbn13] = [capitulo]


    for key in lista_capitulos:
        capitulos = lista_capitulos[key]
        capitulos.sort()
        lista_capitulos[key] = [cap[1] for cap in capitulos]


    return lista_capitulos


def create_document(isis, lista_capitulos):
    monograph_sbid = ''
    edition = ''
    synopsis = ''
    chapte_order = ''
    chapter_title = ''
    chapters_list = []
    chapter_creator = []

    _id = reprbase(int(get(isis, LILACS_IDNUM)))
    title = get(isis, LILACS_TITULO_MONOGRAFICO)

    try:
        isbn = toISBN13(get(isis, LILACS_ISBN, ''))
    except InvalidISBN:
        isbn = get(isis, LILACS_ISBN, 'faltante')
        isbns_invalidos.append((get(isis, LILACS_IDNUM), isbn))

    publisher = get(isis, LILACS_EDITORA)
    edition = get(isis, LILACS_EDICAO)
    year = get(isis, LILACS_DATA_PUBLICACAO)
    doctype = get(isis, LILACS_NIVEL_TRATAMENTO)
    creator = [[('role','author'),('full_name',name['_'])] for name in isis[LILACS_AUTOR_PESSOAL_MONOGRAFICO]]
    shortname = dict(creator[0])['full_name'].split(',')[0].split()[0] #com certeza tem alguma maneira bem mais elegante de fazer isso
    shortname = ''.join((c for c in unicodedata.normalize('NFD', shortname)
                         if unicodedata.category(c) != 'Mn')).lower()
    language = get(isis, LILACS_LANGUAGE)

    if 'a' in doctype:
        doctype = 'Part'
        pages = [('initial', isis[LILACS_PAGINAS_ANALITICO][0].get('f')), ('final', isis[LILACS_PAGINAS_ANALITICO][0].get('l'))]
        try:
            monograph_sbid = isbns_sbid[isbn]
        except KeyError:
            capitulos_sem_sbid_monografica.append((isbn, get(isis, LILACS_IDNUM)))

        chapter_title = get(isis,LILACS_TITULO_ANALITICO)

        try:
            chapter_creator = [[('role','author'),('full_name',name['_'])] for name in isis[LILACS_AUTOR_PESSOAL_ANALITICO]]
        except KeyError:
            chapter_creator = []

        try:
            chapte_order = get(isis, LILACS_ORDEM_CAPITULO)
        except KeyError:
            chapte_order = 999
            capitulos_sem_ordem.append((isbn,get(isis, LILACS_IDNUM)))

    else:
        doctype = 'Monograph'
        pages = get(isis,LILACS_PAGINAS_MONOGRAFICO)
        try:
            synopsis = isis[LILACS_RESUMO][0]['_']
        except KeyError:
            monografias_sem_resumo.append((isbn,get(isis, LILACS_IDNUM)))

        try:
            chapters_list = lista_capitulos[isbn]
        except KeyError:
            monografias_sem_capitulos.append(isbn)

    document = {
        '_id':_id,             #sbid        
        'TYPE':doctype,        #m a mc am a ...
        'isbn':isbn,
        'pages':pages,        
    }



    if doctype == 'Part':
        document.update({
            'creators':chapter_creator,
            'title':chapter_title,    #nivel analitico apenas
            'order':str(chapte_order).zfill(2),    #nivel analitico apenas (campo 902)
            'monograph':monograph_sbid,    #nivel analitico apenas (campo 903)                        
        })

    else:
        document.update({
            'visible':True,
            'edition':edition,
            'shortname':shortname,            
            'title':title,
            'creators':creator,
            'publisher':publisher,
            'language':language,
            'year':year,
            'synopsis':synopsis,        #nivel monografico apenas            
        })

    return document

def get_monograph_cover(sbid):
    #the ugliest thing i've ever done
    name = '/tmp/cover-%s' % sbid
    if not os.path.isfile(name):
        fw = open(name, 'w')
        tmp = urllib2.urlopen('http://img.livros.scielo.org/books/%s/cover/original/cover.jpg' % (sbid))
        fw.write(tmp.read())
        fw.close()

    fr = open(name, 'r')
    return fr

def get_pdf_file(sbid, part):
    #the ugliest thing i've ever done again
    name = '/tmp/pdf-%s-%s' % (sbid, part)
    if not os.path.isfile(name):
        fw = open(name, 'w')
        tmp = urllib2.urlopen('http://img.livros.scielo.org/books/%s/pdf/%s.pdf' % (sbid, part))
        fw.write(tmp.read())
        fw.close()

    fr = open(name, 'r')
    return fr


if __name__ == '__main__':    
    isbns_invalidos = []
    monografias_sem_capitulos = []
    monografias_sem_resumo = []
    capitulos_sem_ordem = []
    capitulos_sem_sbid_monografica = []
    isbns_sbid = {}
    monografias_sem_capa = []
    monografias_sem_pdf = []
    monografias_sem_thumbnail = []
    capitulos_sem_pdf = []

    INPUT_NAME = argv[1]
    
    server = couchdbkit.Server(db_uri)
    db = server.get_or_create_db(db_name)

    with open(INPUT_NAME) as jfile:
        jstruct = json.load(jfile)

    for mono in (mono for mono in jstruct['docs']
                      if 'a' not in get(mono, LILACS_NIVEL_TRATAMENTO)):
        try:
            isbns_sbid[toISBN13(get(mono, LILACS_ISBN, ''))] = reprbase(int(get(mono, LILACS_IDNUM)))
        except InvalidISBN:
            pass

    lista_capitulos = create_chapters_lists(jstruct)
    documents = jstruct['docs']

    for doc in documents:        
        doc_appstruct = create_document(doc, lista_capitulos)
        if doc_appstruct['TYPE'] == 'Monograph':
            monograph = models.Monograph.from_python(doc_appstruct)

            try:
                monograph.cover = {'fp':get_monograph_cover(monograph._id),
                                   'uid':'coveruid',
                                   'filename':'cover.jpg'}
            except urllib2.HTTPError:
                monografias_sem_capa.append(monograph._id)
            else:
                try:
                    monograph.cover_thumbnail = {'fp': create_thumbnail(monograph.cover['fp']),
                                   'filename': 'cover.jpg' + '.thumb.jpeg',
                                   'uid':'',
                                   }
                except IOError:
                    monografias_sem_thumbnail.append(monograph._id)

            try:
                monograph.pdf_file = {'fp':get_pdf_file(monograph._id, monograph.isbn),
                                      'uid':'pdfuid',
                                      'filename':'fulltext.pdf'}
            except urllib2.HTTPError:
                monografias_sem_pdf.append(monograph._id)

            monograph.save(db)

        elif doc_appstruct['TYPE'] == 'Part':
            part = models.Part.from_python(doc_appstruct)
            try:
                part.pdf_file = {'fp':get_pdf_file(part.monograph, part.order),
                                 'uid':'pdfuid',
                                 'filename':'part.pdf'}
            except (urllib2.HTTPError, AttributeError):
                capitulos_sem_pdf.append(part._id)

            part.save(db)

    
    print 'Isbn invalidos: ', isbns_invalidos
    print 'Monografias sem capitulos: ', monografias_sem_capitulos
    print 'monografias_sem_resumo: ', monografias_sem_resumo
    print 'monografias_sem_capa: ', monografias_sem_capa
    print 'monografias_sem_pdf: ', monografias_sem_pdf
    print 'monografias_sem_thumbnail', monografias_sem_thumbnail
    print 'capitulos_sem_ordem: ', capitulos_sem_ordem
    print 'capitulos_sem_sbid_monografica: ', capitulos_sem_sbid_monografica
    print 'capitulos_sem_pdf: ', capitulos_sem_pdf
