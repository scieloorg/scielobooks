import unittest
from indexingdaemon import IndexingDaemon

DB_URI = 'http://localhost:5984'
DB_NAME = 'scielobooks'
SOLR_URI = 'http://localhost:8080/solr'

def print_line(line):
    print 'got %s' % line

class TestIndexingDaemon(unittest.TestCase):
    def setUp(self):
        self.daemon = IndexingDaemon(DB_URI, DB_NAME, SOLR_URI, 'continuous')

    def test_instantiation_wrongpoll(self):
        self.assertRaises(ValueError, IndexingDaemon, DB_URI, DB_NAME, SOLR_URI, 'wrongpoll')

    def test_listening_withcallback(self):
        self.assertEqual('listening stopped', self.daemon.start_listening(timeout=500))


class TestCallback(unittest.TestCase):
    def setUp(self):
        self.notifications = [
            {u'deleted': True, u'changes': [{u'rev': u'3-ad0267dd14975419265f2e1022064741'}], u'id': u'388', u'seq': 1688},
            {u'deleted': True, u'changes': [{u'rev': u'5-93b525131c1d0812f2a99bebd71122d1'}], u'id': u'387', u'seq': 1689},
            {u'changes': [{u'rev': u'8-0af35bda914c6dc9979ad3aa87f7bd2e'}], u'id': u'39h', u'seq': 1693},
            {u'changes': [{u'rev': u'12-5e1264e614b92bb8ff783b2f6ffa13a5'}], u'id': u'3nc', u'seq': 1697},
        ]

    def test_isdeleted(self):
        self.assertTrue(False)