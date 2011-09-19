# encoding: utf-8

import couchdbkit
import urllib2
from datetime import datetime
import pickle
import argparse

class IndexingDaemon(object):
    """
    A daemon that monitors activities in a given CouchDB database
    and keeps its Solr search indexes updated.
    """

    def __init__(self, db_uri, db_name, solr_uri, feed_type, callback=None):
        if feed_type not in ['continuous', 'longpoll']:
            raise ValueError("allowed values are 'continuous' or 'longpoll'. received %s" % feed_type)
        if callback is None:
            callback = self.handle_notification

        self.__db_uri = db_uri
        self.__db_name = db_name
        self.__server = couchdbkit.Server(db_uri)
        self.__db = self.__server[db_name]
        self.__consumer = couchdbkit.Consumer(self.__db)
        self.__solr_uri = solr_uri
        self.__feed_type = feed_type
        self.__callback = callback
        self.__last_activity = None


    def __request_solrxml(self, sbid):
        """
        Request the XML to update a document in Solr
        to a Couchdb show function
        """
        SHOW_FUNCTION = '_design/scielobooks/_show/solr_xml'
        request_url = '/'.join([self.__db_uri, self.__db_name, SHOW_FUNCTION, sbid])

        return urllib2.urlopen(request_url).read()


    def __request_solrserver(self, data):
        update_param = 'update?commit=true'
        request_url = '/'.join([self.__solr_uri, update_param])

        req = urllib2.Request(request_url, data)
        req.add_header('Content-Length', '%d' % len(data))
        req.add_header('Content-Type', 'text/xml; charset=utf-8')

        poster = urllib2.urlopen(req)
        response = poster.read()
        poster.close()


    def store_last_activity(self):
        with open('indexingdaemon.data', 'w') as f:
            pickle.dump(self.last_activity, f)


    @property
    def last_activity(self):
        if self.__last_activity is None:
            try:
                return pickle.load(open('indexingdaemon.data'))
            except (EOFError, IOError):
                return 0
        else:
            return self.__last_activity


    @last_activity.setter
    def last_activity(self, value):
        self.__last_activity = value


    def generate_envelope(self, data):
        MANDATORY_KEYS = ['changes', 'id', 'seq']
        DELETE_TEMPLATE = '<delete><query>sbid:%s</query></delete>'

        for key in MANDATORY_KEYS:
            if key not in data:
                raise ValueError('%s is mandatory' % key)

        if 'deleted' in data:
            return ('delete', DELETE_TEMPLATE % data['id'])

        return ('update', self.__request_solrxml(data['id']))


    def handle_notification(self, notification):
        if not isinstance(notification, dict):
            return None

        try:
            envelope = self.generate_envelope(notification)
        except urllib2.HTTPError:
            print 'Could not generate envelop for %s' % notification['id']
            return None

        try:
            self.__request_solrserver(envelope[1])
        except urllib2.HTTPError:
            print 'Could not send the request to Solr Server for %s' % notification['id']
            return None

        self.last_activity = notification['seq']
        print '%s %s %s' % (datetime.now().isoformat(), envelope[0], notification['id'])


    def start_listening(self, **kwargs):
        print 'start listening for changes in %s' % self.__db_name

        if 'since' not in kwargs:
            kwargs['since'] = self.last_activity

        if self.__feed_type == 'longpoll':
            self.__consumer.wait_once(self.__callback, **kwargs)
        else:
            self.__consumer.wait(self.__callback, **kwargs)

        self.store_last_activity()
        print 'listening stopped'


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='A daemon that monitors activities in a given CouchDB database and keeps its Solr search indexes updated.')

    parser.add_argument('couchdb_uri', metavar='CouchDB-Server-URI', help='CouchDB Server to monitor changes')
    parser.add_argument('db_name', metavar='CouchDB-Database', help='CouchDB Database name')
    parser.add_argument('solr_uri', metavar='Solr-Server-URI', help='Solr Indexing Server')
    parser.add_argument('-hb', '--heartbeat', action='store_true',
                        help='Heartbeat to keep the connection with couchdb alive')
    parser.add_argument('-t', '--feedtype', action='store_true',
                        help='Feed type to monitor changes in a CouchDB Database (continuous|longpoll)')

    args = parser.parse_args()

    heartbeat = args.heartbeat if args.heartbeat else 10000
    feedtype = args.feedtype if args.feedtype else 'continuous'

    daemon = IndexingDaemon(args.couchdb_uri, args.db_name, args.solr_uri, feedtype)
    daemon.start_listening(heartbeat=heartbeat)