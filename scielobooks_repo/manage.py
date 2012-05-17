#!/usr/bin/env python
from migrate.versioning.shell import main

if __name__ == '__main__':
    main(url='postgresql+psycopg2://postgres:123456@localhost/scielobooks', debug='False', repository='scielobooks_repo')
