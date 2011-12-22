import os
import sys
from setuptools import setup, find_packages
try:
    from scielobooks import APP_VERSION
except ImportError:
    APP_VERSION = ''


if sys.version_info[:2] != (2, 7):
    raise RuntimeError('Requires Python 2.7')

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.txt')).read()
    CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()
except IOError:
    README = CHANGES = ''

requires = [
    'pyramid<=1.0.2',
    'WebError',
    'Babel',
    'pyramid_zcml',
    'colander',
    'deform<=0.9.3',
    'couchdbkit',
    'PIL',
    'isisdm',
    'SQLAlchemy',
    'pyramid_handlers',
    'pycrypto',
    'pyramid_mailer',
    'couchapp',
    'chameleon<1.999',
    'psycopg2',
    'setuptools-git',
    ]

setup(name = 'scielobooks',
      version = APP_VERSION,
      description = 'scielobooks',
      long_description = README + '\n\n' +  CHANGES,
      classifiers = [
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author = 'BIREME/OPAS/OMS',
      author_email = 'isisnbp-devel@listas.bireme.br',
      url = 'http://reddes.bvsalud.org/projects/scielo-books',
      keywords = 'web scielo scielobooks',
      packages = find_packages(),
      include_package_data = True,
      zip_safe = False,
      install_requires = requires,
      tests_require = ['Nose'],
      test_suite = "scielobooks",
      entry_points = """\
      [paste.app_factory]
      main = scielobooks:main
      """,
      paster_plugins = ['pyramid'],
      message_extractors = { 'scielobooks': [
            ('**.py','chameleon_python', None ),
            ('**.pt','chameleon_xml', None ),
            ]
        },

      )

# ``setuptools-git`` in order to build packages based on git repositories.