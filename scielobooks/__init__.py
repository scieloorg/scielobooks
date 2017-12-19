# coding: utf-8
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
APP_VERSION = '1.1.0'

DEFAULT_SETTINGS = [
    ('available_languages', 'AVAILABLE_LANGUAGES', str, 'pt en es'),
    ('fileserver_sync_enable', 'FILESERVER_SYNC_ENABLE', bool, 'true'),
    ('fileserver_url', 'FILESERVER_URL', str, 'http://static.scielo.org/scielobooks'),
    ('fileserver_remotebase', 'FILESERVER_REMOTEBASE', str, '/var/www/static_scielo_org/scielobooks'),
    ('fileserver_host', 'FILESERVER_HOST', str, '192.168.1.12'),
    ('fileserver_username', 'FILESERVER_USERNAME', str, ''),
    ('fileserver_password', 'FILESERVER_PASSWORD', str, ''),
    ('sqlalchemy.url', 'SQLALCHEMY_URL', str, 'sqlite:///%(here)s/database.db'),
    ('sqlalchemy.pool_size', 'SQLALCHEMY_POOL_SIZE', int, 4),
    ('sqlalchemy.pool_recycle', 'SQLALCHEMY_POOL_RECYCLE', int, 3600),
    ('books_static_url', 'BOOKS_STATIC_URL', str, 'http://img.livros.scielo.org/books'),
    ('solr_url', 'SOLR_URL', str, 'http://iahx.local'),
    ('db_uri', 'DB_URI', str, 'http://127.0.0.1:5984'),
    ('db_name', 'DB_NAME', str, 'scielobooks_1a'),
    ('serve_static_files', 'SERVER_STATIC_FILES', bool, 'true'),
    ('mail.host', 'MAIL_HOST', str, 'mail_server_address'),
    ('mail.port', 'MAIL_PORT', str, '25'),
    ('mail.username', 'MAIL_USERNAME', str, ''),
    ('mail.password', 'MAIL_PASSWORD', str, ''),
    ('mail.default_sender', 'MAIL_DEFAULT_SENDER', str, ''),
    ('mail.tls', 'MAIL_TLS', str, 'true'),
]


def parse_settings(settings):
    """Analisa e retorna as configurações da app com base no arquivo .ini e env.
    As variáveis de ambiente possuem precedência em relação aos valores
    definidos no arquivo .ini.
    """
    parsed = {}
    cfg = list(DEFAULT_SETTINGS)

    for name, envkey, convert, default in cfg:
        value = os.environ.get(envkey, settings.get(name, default))
        if convert is not None:
            value = convert(value)
        parsed[name] = value

    return parsed


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    authentication_policy = AuthTktAuthenticationPolicy('seekrit', callback=groupfinder)
    authorization_policy = ACLAuthorizationPolicy()

    engine = engine_from_config(settings, prefix='sqlalchemy.')
    db_maker = sessionmaker(bind=engine)

    config = Configurator(settings=parse_settings(settings),
                          root_factory='scielobooks.resources.RootFactory',
                          authentication_policy=authentication_policy,
                          authorization_policy=authorization_policy,
                          request_factory=MyRequest,
                          renderer_globals_factory=renderer_globals_factory)

    config.registry.settings['rel_db.sessionmaker'] = db_maker
    config.include(pyramid_zcml)
    config.load_zcml('configure.zcml')
    config.include('pyramid_mailer')
    config.include('pyramid_celery')

    config.registry['mailer'] = Mailer.from_settings(settings)
    config.registry['app_version'] = APP_VERSION

    db_uri = config.registry.settings['db_uri']
    conn = couchdbkit.Server(db_uri)
    config.registry.settings['db_conn'] = conn
    config.add_subscriber(add_couch_db, NewRequest)

    config.scan('scielobooks.models')
    initialize_sql(engine)

    if config.registry.settings['serve_static_files'] is True:
        config.add_static_view(name='static', path='static')
    config.add_static_view('deform_static', 'deform:static')
    config.add_static_view('/'.join((config.registry.settings['db_uri'], config.registry.settings['db_name'])), 'scielobooks:database')
    config.add_static_view(config.registry.settings['fileserver_url'], 'scielobooks:fileserver')

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