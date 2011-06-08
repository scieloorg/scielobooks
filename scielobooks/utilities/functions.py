# coding: utf-8

# Except from:
# http://flask.pocoo.org/snippets/5/
# Generating Slugs
# By Armin Ronacher filed in URLs 

import re
from unicodedata import normalize

_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')

def slugify(text, delim=u'-'):
    """Generates an slightly worse ASCII-only slug."""
    result = []
    for word in _punct_re.split(text.lower()):
        word = normalize('NFKD', word).encode('ascii', 'ignore')
        if word:
            result.append(word)
    return unicode(delim.join(result))
