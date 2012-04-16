# coding: utf-8
import StringIO
import tempfile
import os
import re
from unicodedata import normalize

import Image
import deform
import paramiko
from celery.task import task
try:
    import gfx
except ImportError:
    # raise ImportError('http://www.swftools.org/gfx_tutorial.html')
    print 'Whithout gfx module the system is not able to handle pdf to swf conversions'

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
        try:
            word = normalize('NFKD', word.decode()).encode('ascii', 'ignore')
        except UnicodeEncodeError:
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
    gfx.setparameter('poly2bitmap', '1')
    doc = gfx.open("pdf", pdf_temp_filename)
    swf = gfx.SWF()
    swf.setparameter('flashversion', '9')
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


class SFTPChannel(object):
    """
    Opens a sftp session to transfer static files to the
    static webserver
    """
    def __init__(self, remote_host, username, password, port=22):
        self.remote_host = remote_host
        self.username = username
        self.password = password
        self.port = port

    def __enter__(self):
        self.transport = paramiko.Transport((self.remote_host, self.port))
        self.transport.connect(username=self.username, password=self.password) #raises paramiko.SSHException
        self.sftp = paramiko.SFTPClient.from_transport(self.transport)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            self.transport.close()
        except:
            pass
        
    def transfer(self, data, remote_path):
        if not isinstance(data, basestring):
            data = data.read()

        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.write(data)
        self.temp_filename = self.temp_file.name
        self.temp_file.close()

        if remote_path.startswith('/'):
            splitted_remote_path = remote_path[1:]
        splitted_remote_path = splitted_remote_path.split('/')[:-1]

        current_path = '/'
        for path_segment in splitted_remote_path:
            current_path += path_segment   
            try:
                self.sftp.mkdir(current_path)
            except IOError:
                pass #assuming the directory already exists
            current_path += '/'
    
        self.sftp.put(self.temp_filename, remote_path)


def transfer_static_file(request, data, book_sbid, filename, filetype, remote_basepath):
    """
    Start a celery task to transfer the file to the static webserver.

    We are using a closure just to make the code more simple, because the
    request object is not serializable by the celery tasks.
    """
    remote_path = os.path.join(remote_basepath, book_sbid, filetype,
    '.'.join([filename, filetype]))
    fileserver_host = request.registry.settings['fileserver_host']
    fileserver_username = request.registry.settings['fileserver_username']
    fileserver_password = request.registry.settings['fileserver_password']

    return transfer_data.delay(data.read(), remote_path, fileserver_host, 
        fileserver_username, fileserver_password)

@task(name='functions.transfer_data')
def transfer_data(data, remote_path, fileserver_host, fileserver_username, fileserver_password):
    logger = transfer_data.get_logger()
    try:
        with SFTPChannel(fileserver_host, fileserver_username, fileserver_password) as sftp:
            logger.info('Transfering %s to %s' % (remote_path, fileserver_host))
            sftp.transfer(data, remote_path)
    except Exception, exc:
        logger.error('Error transfering %s to %s: %s' % (remote_path, fileserver_host, exc))
