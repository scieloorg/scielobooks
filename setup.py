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

requires = []

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
      url = 'http://github.com/bireme/scielobooks',
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
