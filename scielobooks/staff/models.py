from isis import model
import deform
import urllib2


class Monograph(model.CouchdbDocument):
    visible = model.BooleanProperty()
    title = model.TextProperty(required=True)
    isbn = model.TextProperty(required=True)
    creators = model.MultiCompositeTextProperty(subkeys=['full_name','role',])
    publisher = model.TextProperty(required=True)
    language = model.TextProperty(choices=(('pt', 'portugues'), ('en', 'ingles')))
    year = model.TextProperty()
    pages = model.TextProperty()
    edition = model.TextProperty()
    shortname = model.TextProperty()
    collection = model.TextProperty()
    format = model.TextProperty()
    cover = model.FileProperty()
    cover_thumbnail = model.FileProperty()
    book = model.TextProperty()
    synopsis = model.TextProperty()
    about_author = model.MultiCompositeTextProperty(subkeys=['full_name','about',])
    translators = model.MultiTextProperty()
    pdf_url = model.TextProperty()
    serie = model.TextProperty()
    
    class Meta:
        hide = ('evaluation', 'cover_thumbnail')

class Part(model.CouchdbDocument):
    title = model.TextProperty(required=True)
    order = model.TextProperty(required=True)
    creators = model.MultiCompositeTextProperty(required=False, subkeys=['full_name', 'role'])
    monograph = model.TextProperty(required=False)

    class Meta:
        hide = ('monograph',)