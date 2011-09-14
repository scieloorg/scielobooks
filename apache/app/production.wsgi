from pyramid.paster import get_app
application = get_app(
  '/home/aplicacoes-scielo/scielobooks/production.ini',
  'main')
