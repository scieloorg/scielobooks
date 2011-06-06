from isis import model
import deform
import urllib2


class Evaluation(model.CouchdbDocument):
    monograph = model.TextProperty() #model.ReferenceProperty()
    publisher_url = model.TextProperty(required=False)
    publisher = model.TextProperty()
    title = model.TextProperty()
    editorial_decision = model.FileProperty(required=False)
    committee_decision = model.MultiCompositeTextProperty()
    opinions = model.MultiCompositeTextProperty()
    toc = model.FileProperty(required=False)
    meetings = model.MultiTextProperty()
    status = model.TextProperty()
    theme = model.TextProperty()

    class Meta:
        hide = ('monograph', 'publisher', 'title',)

class Monograph(model.CouchdbDocument):
    visible = model.BooleanProperty(required=False)
    evaluation = model.TextProperty() #model.ReferenceProperty()
    title = model.TextProperty(required=True)
    isbn = model.TextProperty(required=True)
    creators = model.MultiCompositeTextProperty(subkeys=['full_name','role',])
    publisher = model.TextProperty(required=True)
    language = model.TextProperty(choices=(('pt', 'portugues'), ('en', 'ingles')))
    year = model.TextProperty()
    pages = model.TextProperty()
    edition = model.TextProperty()
    shortname = model.TextProperty()
    download_formats = model.MultiTextProperty(required=False)
    collection = model.TextProperty()
    format = model.TextProperty()
    cover = model.FileProperty()
    book = model.TextProperty()
    #chapters_list = model.MultiCompositeTextProperty()
    synopsis = model.TextProperty()
    #about_author = model.CompositeTextProperty()
    translators = model.MultiTextProperty()
    pdf_url = model.TextProperty()
    serie = model.TextProperty()
    
    class Meta:
        hide = ('evaluation',)

class Part(model.CouchdbDocument):
    title = model.TextProperty(required=True)
    order = model.TextProperty(required=True)
    creators = model.MultiCompositeTextProperty(required=False, subkeys=['full_name', 'role'])
    monograph = model.TextProperty(required=False)

    class Meta:
        hide = ('monograph',)