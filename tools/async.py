from twisted.internet import reactor
from twisted.web import client
import json

DB_URL = 'http://localhost:5984/scielobooks_1a/'
DOCS_DIR = '/tmp/docs/'

def documents_list():
    deferred = client.getPage(DB_URL + '_design/export/_view/all_docs')
    deferred.addCallback(documents_listed).addErrback(error, 'documents_list')

def documents_listed(result):
    for id in [item['id'] for item in json.loads(result)['rows']]:
        url = str(DB_URL+id)
        print url
        deferred = client.getPage(url)
        deferred.addCallback(document_downloaded).addErrback(error, 'documents_listed')
    print 'documents_listed: DONE'

def error(error, function):
    print '(%s) Ops!, %s' % (function, error)
    reactor.stop()

def document_downloaded(docstr):
    id = json.loads(docstr)['_id']
    with open(DOCS_DIR+id, 'wb') as out:
        out.write(docstr)

def main():
    reactor.callLater(0, documents_list)
    print 'reactor start'
    reactor.run()
    print 'reactor stop'

if __name__ == '__main__':
    main()

