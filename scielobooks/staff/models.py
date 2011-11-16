from isis import model
import deform
import urllib2
from collections import OrderedDict
import copy

class Monograph(model.CouchdbDocument):
    title = model.TextProperty(required=True)
    isbn = model.TextProperty(required=True)
    creators = model.MultiCompositeTextProperty(subkeys=['role','full_name', 'link_resume'], required=True)
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
    doi_number = model.TextProperty()
    notes = model.TextProperty()
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

    def _creators_by_roles(self):
        creators_by_role = OrderedDict()
        for creator in self.creators:
            creators_by_role.setdefault(creator['role'], []).append(creator['full_name'])

        return copy.deepcopy(creators_by_role)

    def formatted_creators(self, formatting_func=None):
        # {'author': 'Babbage, Charles; Turing, Alan.'}
        if formatting_func is None:
            def formatting_func(creators):
                """
                accept a list of creators and returns it in a formatted form.
                """
                return '; '.join(creators)

        creators_by_role = self._creators_by_roles()

        return OrderedDict((key, formatting_func(value)) for key, value in creators_by_role.items())

    @property
    def shortname(self):
        shortname_format = '%s-%s'
        creators_by_role = self._creators_by_roles()
        if 'corporate_author' in creators_by_role:
            return shortname_format % (creators_by_role['corporate_author'][0].lower(), self.isbn)
        elif 'individual_author' in creators_by_role:
            first_author = creators_by_role['individual_author'][0]
            first_author_lastname = first_author[:first_author.find(',')] if ',' in first_author else first_author_lastname.split()[0]

            return shortname_format % (first_author_lastname.lower(), self.isbn)
        else:
            raise AttributeError()


class Part(model.CouchdbDocument):
    title = model.TextProperty(required=True)
    order = model.TextProperty()
    creators = model.MultiCompositeTextProperty(required=False, subkeys=['role','full_name', 'link_resume'])
    pages = model.CompositeTextProperty(subkeys=['initial','final',])
    pdf_file = model.FileProperty()
    descriptive_information = model.TextProperty()
    text_language = model.TextProperty()
    notes = model.TextProperty()

    monograph = model.TextProperty(required=False)
    monograph_title = model.TextProperty(required=False)
    monograph_isbn = model.TextProperty(required=True)
    monograph_creators = model.MultiCompositeTextProperty(subkeys=['role','full_name', 'link_resume'])
    monograph_publisher = model.TextProperty(required=True)
    monograph_language = model.TextProperty()
    monograph_year = model.TextProperty()
    visible = model.BooleanProperty()

    class Meta:
        hide = ('monograph', 'monograph_title', 'monograph_isbn', 'monograph_creators',
            'monograph_publisher', 'monograph_language', 'monograph_year', 'visible')
