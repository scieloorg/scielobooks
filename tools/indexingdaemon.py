import couchdbkit

def print_line(line):
    print 'got %s' % line

class IndexingDaemon(object):
    def __init__(self, db_uri, db_name, solr_uri, feed_type, callback=None):
        if feed_type not in ['continuous', 'longpoll']:
            raise ValueError("allowed values are 'continuous' or 'longpoll'. received %s" % feed_type)
        if callback is None:
            callback = print_line

        self._server = couchdbkit.Server(db_uri)
        self._db = self._server[db_name]
        self._consumer = couchdbkit.Consumer(self._db)
        self._solr_uri = solr_uri
        self._feed_type = feed_type
        self._callback = callback

    def start_listening(self, callback=None, **kwargs):

        if self._feed_type == 'longpoll':
            self._consumer.wait_once(self._callback, **kwargs)
        else:
            self._consumer.wait(self._callback, **kwargs)

        return 'listening stopped'
