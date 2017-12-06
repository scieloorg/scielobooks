import os

from pyramid.config import Configurator
from pyramid.events import subscriber
from pyramid.events import NewRequest
from pyramid.events import NewResponse
from pyramid.events import BeforeRender
from pyramid.i18n import get_localizer
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.exceptions import Forbidden
from pyramid_mailer.mailer import Mailer
from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker
import couchdbkit
import pyramid_zcml

from .views import custom_forbidden_view
from .security import groupfinder
from .models import initialize_sql
from scielobooks.request import MyRequest


APP_PATH = os.path.abspath(os.path.dirname(__file__))
APP_VERSION = 'v1'


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
                          request_factory=MyRequest,
                          renderer_globals_factory=renderer_globals_factory)

    config.include(pyramid_zcml)
    config.load_zcml('configure.zcml')
    config.include('pyramid_mailer')
    config.include('pyramid_celery')

    config.registry['mailer'] = Mailer.from_settings(settings)
    config.registry['app_version'] = APP_VERSION

    db_uri = settings['db_uri']
    conn = couchdbkit.Server(db_uri)
    config.registry.settings['db_conn'] = conn
    config.add_subscriber(add_couch_db, NewRequest)

    config.scan('scielobooks.models')
    initialize_sql(engine)

    if settings['serve_static_files'] == 'true':
        config.add_static_view(name='static', path='static')
    config.add_static_view('deform_static', 'deform:static')
    config.add_static_view('/'.join((settings['db_uri'], settings['db_name'])), 'scielobooks:database')
    config.add_static_view(settings['fileserver_url'], 'scielobooks:fileserver')

    config.add_view(custom_forbidden_view, context=Forbidden)

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


def renderer_globals_factory(system):
    """
    Injects values to renderer globals before it is sent to the renderer.

    http://docs.pylonsproject.org/projects/pyramid/en/1.0-branch/narr/hooks.html#adding-renderer-globals
    """
    return {'current_language': get_localizer(system['request']).locale_name,}