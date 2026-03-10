import os

from setuptools import setup, find_packages

requires = [
    'pyramid==2.0.2',
    'pyramid-mailer>=0.15.1',
    'pyramid-debugtoolbar>=4.12.1',
    'pyramid-chameleon>=0.3',
    'SQLAlchemy>=1.4,<2.0',
    'deform>=2.0.15',
    'colander>=2.0',
    'Pillow>=10.0.0',
    'psycopg2-binary>=2.9.9',
    'waitress>=3.0.0',
    'gunicorn>=22.0.0',
    'transaction>=5.0',
    'paramiko>=3.4.0',
]
here = os.path.abspath(os.path.dirname(__file__))


try:
    from scielobooks import APP_VERSION
except ValueError:
    APP_VERSION = '1.1.1'


try:
    with open(os.path.join(here, 'README.txt'), encoding='utf-8') as readme_file:
        README = readme_file.read()
    with open(os.path.join(here, 'CHANGES.txt'), encoding='utf-8') as changes_file:
        CHANGES = changes_file.read()
except IOError:
    README = CHANGES = ''


setup(name = 'scielobooks',
      version = APP_VERSION,
      description = 'scielobooks',
      long_description = README + '\n\n' +  CHANGES,
      classifiers = [
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.12",
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
      python_requires = ">=3.12",
      install_requires = requires,
      tests_require = ['Nose'],
      test_suite = "scielobooks",
      entry_points = """\
      [paste.app_factory]
      main = scielobooks:main
      """,
      paster_plugins = ['pyramid'],
      message_extractors = { 'scielobooks': [
            ('**.py','lingua_python', None ),
            ('**.pt','lingua_xml', None ),
            ]
        },

      )

# ``setuptools-git`` in order to build packages based on git repositories.
