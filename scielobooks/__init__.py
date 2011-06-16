from pyramid.config import Configurator
from pyramid.events import subscriber
from pyramid.events import NewRequest, NewResponse
from pyramid.i18n import get_localizer
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker

import couchdbkit
import pyramid_zcml

from .security import groupfinder
from .models import initialize_sql
from scielobooks.request import MyRequest


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    authentication_policy = AuthTktAuthenticationPolicy('seekrit', callback=groupfinder)
    authorization_policy = ACLAuthorizationPolicy()
    
    engine = engine_from_config(settings, prefix='sqlalchemy.')
    db_maker = sessionmaker(bind=engine)
    settings['rel_db.sessionmaker'] = db_maker

    config = Configurator(settings=settings,
                          root_factory='scielobooks.resources.RootFactory',
                          authentication_policy=authentication_policy,
                          authorization_policy=authorization_policy,
                          request_factory=MyRequest)

    config.include(pyramid_zcml)
    config.load_zcml('configure.zcml')

    db_uri = settings['db_uri']
    conn = couchdbkit.Server(db_uri)
    config.registry.settings['db_conn'] = conn
    config.add_subscriber(add_couch_db, NewRequest)

    config.scan('scielobooks.models')
    initialize_sql(engine)

    if settings['serve_static_files'] == 'true':
        config.add_static_view(name='static', path='static')
    config.add_static_view('deform_static', 'deform:static')
    config.add_static_view(settings['books_static_url'], 'scielobooks:books')
    config.add_static_view('/'.join((settings['db_uri'], settings['db_name'])), 'scielobooks:database')

    config.add_translation_dirs('scielobooks:locale/')
    config.set_locale_negotiator(custom_locale_negotiator)

    my_session_factory = UnencryptedCookieSessionFactoryConfig('itsaseekreet')
    config.set_session_factory(my_session_factory)

    return config.make_wsgi_app()

def add_couch_db(event):
    settings = event.request.registry.settings
    db = settings['db_conn'][settings['db_name']]
    event.request.db = db

def custom_locale_negotiator(request):
    settings = request.registry.settings
    locale = ''

    if 'language' in request.params:
        locale = request.params['language']
    elif 'language' in request.cookies.keys():
        locale = request.cookies['language']

    if locale not in settings['available_languages'].split():
        locale = settings['default_locale_name']

    return locale
