from pyramid.paster import get_app
application = get_app(
  '/var/www/livros_scielo_org/scielobooks/production.ini',
  'main')
