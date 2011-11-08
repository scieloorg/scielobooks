# coding: utf-8
from lxml import etree as ET
from urllib import urlencode, urlopen
import httplib2

#Couchdb
DB_SERVER = 'http://127.0.0.1:5984'
DB_NAME = 'scielobooks_1a'
SOURCE_DOC_URL = '/'.join([DB_SERVER, DB_NAME, '_design/scielobooks/_show/solr_xml/%s'])

#Others
PDF_SERVER = 'http://img.livros.scielo.org/books/%s/pdf/%s.pdf'


def get_request_args(xml):
    arg_list = []
    xml_object = ET.fromstring(xml)

    for doc in xml_object.findall('doc'):
        get_args = dict((elem.attrib['name'], elem.text.encode('iso-8859-1')) for elem in doc.iterchildren() if elem.text)
        arg_list.append(get_args)

    return arg_list if len(arg_list) > 1 else arg_list[0]


def fetch_doc(sbid):
    #FIXME: Raise an exception when a doc is not retrieved
    xml_string = urlopen(SOURCE_DOC_URL % sbid).read()

    return xml_string


def fetch_pdf(sbid):
    isbn = get_value(fetch_doc(sbid), 'isbn')

    return urlopen(PDF_SERVER % (sbid, isbn))


def get_value(xml, field_name):
    xml_object = ET.fromstring(xml)
    value = unicode(xml_object.xpath('.//field[@name="%s"]' % field_name)[0].text).strip()

    return value


class SolrFeeder(object):
    def __init__(self, solr_url):
        if urlopen(solr_url).getcode() != 200:
            raise SolrError('Solr server is not valid')
        self.solr_url = solr_url

    def feed(self, sbid):
        #data = get_request_args(fetch_doc(sbid))
        data = fetch_doc(sbid)
        self.update(data)

        return self

    def commit(self):
        data = '<commit waitFlush="true" waitSearcher="true"/>'
        self.update(data)

    def update(self, data):
        URL = self.solr_url + '/update'

        h = httplib2.Http()
        resp, content = h.request(URL,
                                  'POST',
                                  data,
                                  headers={'Content-Type':'text/xml; charset=utf-8'})

        if resp['status'] != '200':
            raise SolrError(resp, content)

class SolrError(Exception):
    pass

