from isis import model

class Evaluation(model.CouchdbDocument):
    monograph = model.TextProperty() #model.ReferenceProperty()
    publisher_url = model.TextProperty()
    publisher = model.TextProperty()
    title = model.TextProperty()
    editorial_decision = model.TextProperty()
    cover = model.TextProperty()
    #committee_decision = model.MultiCompositeTextProperty()
    #opinions = model.MultiCompositeTextProperty()
    toc = model.TextProperty()
    meetings = model.MultiTextProperty()
    status = model.TextProperty()
    theme = model.TextProperty()

    class Meta:
        hide = ('monograph',)

class Monograph(model.CouchdbDocument):
    visible = model.TextProperty()
    evaluation = model.TextProperty() #model.ReferenceProperty()
    title = model.TextProperty()
    isbn = model.TextProperty()
    #creators = MultiCompositeTExtProperty()
    publisher = model.TextProperty()
    language = model.TextProperty()
    year = model.TextProperty()
    pages = model.TextProperty()
    edition = model.TextProperty()
    shortname = model.TextProperty()
    download_formats = model.MultiTextProperty()
    collection = model.TextProperty()
    format = model.TextProperty()
    cover = model.TextProperty()
    book = model.TextProperty()
    #chapters_list = MultiCompositeTextProperty()
    synopsis = model.TextProperty()
    #about_author = MultiCompositeTextProperty()
    translators = model.MultiTextProperty()
    pdf_url = model.TextProperty()
    serie = model.TextProperty()