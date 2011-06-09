# coding: utf-8


import re
from unicodedata import normalize
import Image
import StringIO

_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')

def slugify(text, delim=u'-'):
    """Generates an slightly worse ASCII-only slug.
    Originally from:
    http://flask.pocoo.org/snippets/5/
    Generating Slugs
    By Armin Ronacher filed in URLs 
    """
    result = []
    for word in _punct_re.split(text.lower()):
        word = normalize('NFKD', word).encode('ascii', 'ignore')
        if word:
            result.append(word)
    return unicode(delim.join(result))


def create_thumbnail(img, size=None):

    if not size:
        size = (160, 160)
    
    if not isinstance(img, basestring):
        try:
            img = img.read()
        except AttributeError:
            return None
    
    img_thumb = Image.open(StringIO.StringIO(img))
    img_thumb.thumbnail(size, Image.ANTIALIAS)
    img_thumb.save('/tmp/scilothumb.jpg')
    #FOR LORD, FIX ME!!!!
    return open('/tmp/scilothumb.jpg')
