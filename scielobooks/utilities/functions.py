# coding: utf-8
import re
from unicodedata import normalize
import Image
import StringIO
import tempfile
import os
import deform
try:
    import gfx
except ImportError:
    raise ImportError('http://www.swftools.org/gfx_tutorial.html')

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
    buf = StringIO.StringIO()
    img_thumb.save(buf, format='JPEG')

    return buf

def convert_pdf2swf(pdf_doc):

    if not isinstance(pdf_doc, basestring):
        try:
            pdf_doc = pdf_doc.read()
        except AttributeError:
            return None
    pdf_temp_file = tempfile.NamedTemporaryFile(delete=False)
    swf_temp_file = tempfile.NamedTemporaryFile(delete=False)

    pdf_temp_filename = pdf_temp_file.name
    swf_temp_filename = swf_temp_file.name

    pdf_temp_file.write(pdf_doc)
    pdf_temp_file.close()
    swf_temp_file.close()

    doc = gfx.open("pdf", pdf_temp_filename)
    swf = gfx.SWF()
    buf = StringIO.StringIO()
    for pagenr in range(1,doc.pages+1):
        page = doc.getPage(pagenr)
        swf.startpage(page.width, page.height)
        page.render(swf)
        swf.endpage()
    swf.save(swf_temp_filename)

    os.unlink(pdf_temp_filename)

    return open(swf_temp_filename, 'r')

def customize_form_css_class(form, default_css=None, **kwargs):
    """
    Sets CSS classes to form widgets.

    If a ``default_css`` arg is passed, all widgets' css_class attr
    will be set with it, except field names in kwargs.
    """
    if not isinstance(form, deform.form.Form):
        raise TypeError('Expecting an instance of deform.form.Form')

    if default_css or kwargs:
        for field in form:
            field.widget.css_class = kwargs[field.name] if field.name in kwargs else default_css

def remove_none_values_from_dict(d):
    return dict([(key,d[key]) for key in d if d[key]])
