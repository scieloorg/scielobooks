from twisted.internet import reactor
from twisted.web import client
from twisted.web.http_headers import Headers
import json

from zope.interface import implements
from twisted.internet.defer import succeed
from twisted.web.iweb import IBodyProducer


SOLR_URL = 'http://localhost:8080/scielobooks'
DB_URL = 'http://localhost:5984/scielobooks/'


class StringProducer(object):
    implements(IBodyProducer)

    def __init__(self, body):
        self.body = body
        self.length = len(body)

    def startProducing(self, consumer):
        consumer.write(self.body)
        return succeed(None)

    def pauseProducing(self):
        pass

    def stopProducing(self):
        pass


def documents_list():
    deferred = client.getPage(DB_URL + '_design/scielobooks/_view/docs_to_index')
    deferred.addCallback(documents_listed).addErrback(error, 'documents_list')

def documents_listed(result):
    for i, id in enumerate([item['id'] for item in json.loads(result)['rows']]):
        reactor.callLater(0.05 * i, document_download, id)

def error(error, function):
    print '(%s) Ops!, %s' % (function, error)
    reactor.stop()

def document_download(id):
    url = str(DB_URL+ '_design/scielobooks/_show/solr_xml/'+id)
    deferred = client.getPage(url)
    deferred.addCallback(document_downloaded, id).addErrback(error, 'document_download')

def document_downloaded(docstr, id):
    URL = SOLR_URL + '/update?commit=true'

    agent = client.Agent(reactor)
    deferred = agent.request(
        uri=URL,
        method='POST',
        bodyProducer=StringProducer(docstr),
        headers=Headers({'Content-Type':['text/xml; charset=utf-8']})
    )
    deferred.addCallback(document_indexed, id).addErrback(error, 'document_downloaded')

def document_indexed(result, id):
    print "Indexed: %s" % id

def main():
    reactor.callLater(0, documents_list)
    print 'reactor start'
    reactor.run()
    print 'reactor stop'

if __name__ == '__main__':
    main()
