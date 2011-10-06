from isis import model
import deform
import urllib2


class Monograph(model.CouchdbDocument):
    title = model.TextProperty(required=True)
    isbn = model.TextProperty(required=True)
    creators = model.MultiCompositeTextProperty(subkeys=['role','full_name', 'link_resume'])
    publisher = model.TextProperty(required=True)
    publisher_url = model.TextProperty()
    language = model.TextProperty()
    synopsis = model.TextProperty()
    year = model.TextProperty()
    city = model.TextProperty()
    country = model.TextProperty()
    pages = model.TextProperty()
    primary_descriptor = model.TextProperty()
    edition = model.TextProperty()
    collection = model.CompositeTextProperty(subkeys=['individual_author', 'corporate_author', 'title', 'english_translated_title', 'total_number_of_volumes'])
    format = model.CompositeTextProperty(subkeys=['height', 'width'])
    serie = model.CompositeTextProperty(subkeys=['title', 'issue', 'issue_number', 'issn'])
    use_licence = model.TextProperty()
    pdf_file = model.FileProperty()
    epub_file = model.FileProperty()
    cover = model.FileProperty()
    toc = model.FileProperty()
    editorial_decision = model.FileProperty()

    cover_thumbnail = model.FileProperty()
    visible = model.BooleanProperty()
    creation_date = model.TextProperty()
    created_by = model.TextProperty() #TODO

    class Meta:
        hide = ('cover_thumbnail', 'visible', 'creation_date', 'created_by')


class Part(model.CouchdbDocument):
    title = model.TextProperty(required=True)
    order = model.TextProperty()
    creators = model.MultiCompositeTextProperty(required=False, subkeys=['role','full_name', 'link_resume'])
    pages = model.CompositeTextProperty(subkeys=['initial','final',])
    pdf_file = model.FileProperty()
    descriptive_information = model.TextProperty()
    text_language = model.TextProperty()

    monograph = model.TextProperty(required=False)

    class Meta:
        hide = ('monograph',)
