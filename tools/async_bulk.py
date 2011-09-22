from twisted.internet import reactor
from twisted.web import client
import json

DB_URL = 'http://localhost:5984/scielobooks_1a/'
DOCS_DIR = '/tmp/docs/'

def documents_list():
    deferred = client.getPage(DB_URL + '_design/export/_view/all_docs')
    deferred.addCallback(documents_listed).addErrback(error, 'documents_list')

def documents_listed(result):
    for i, id in enumerate([item['id'] for item in json.loads(result)['rows']]):
        reactor.callLater(0.1 * i, document_download, id)


def error(error, function):
    print '(%s) Ops!, %s' % (function, error)
    reactor.stop()

def document_download(id):
    url = str(DB_URL+ '_design/scielobooks/_show/solr_xml/'+id)
    #print url
    deferred = client.getPage(url)
    deferred.addCallback(document_downloaded, id).addErrback(error, 'document_download')

def document_downloaded(docstr, id):
    with open(DOCS_DIR+id, 'wb') as out:
        out.write(docstr)

def main():
    reactor.callLater(0, documents_list)
    print 'reactor start'
    reactor.run()
    print 'reactor stop'

if __name__ == '__main__':
    main()

