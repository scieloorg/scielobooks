from isis import model
import deform
import urllib2
from collections import OrderedDict
from ..utilities import functions
import copy

class Monograph(model.CouchdbDocument):
    title = model.TextProperty(required=True)
    translated_titles = model.MultiCompositeTextProperty(subkeys=['title','language'])
    isbn = model.TextProperty(required=True)
    creators = model.MultiCompositeTextProperty(subkeys=['role','full_name', 'link_resume'])
    publisher = model.TextProperty(required=True)
    publisher_url = model.TextProperty()
    language = model.TextProperty()
    synopsis = model.TextProperty()
    translated_synopses = model.MultiCompositeTextProperty(subkeys=['synopsis','language'])
    year = model.TextProperty()
    city = model.TextProperty()
    country = model.TextProperty()
    pages = model.TextProperty()
    primary_descriptor = model.TextProperty()
    translated_primary_descriptors = model.MultiCompositeTextProperty(subkeys=['primary_descriptor','language'])
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
                if len(creators) > 3:
                    return creators[0] + ' et al.'

                return '; '.join(creators)

        creators_by_role = self._creators_by_roles()

        return OrderedDict((key, formatting_func(value)) for key, value in creators_by_role.items())

    def __get_cleaned_lastname(self, author):
        return functions.slugify(author).split('-')[0]

    @property
    def shortname(self):
        shortname_format = '%s-%s'
        creators_by_role = self._creators_by_roles()
        precedence = ('individual_author', 'organizer', 'coordinator', 'translator', 'collaborator', 'editor', 'corporate_author', 'other')
        for role in precedence:
            if role in creators_by_role:
                first_author = creators_by_role[role][0]
                first_author_lastname = self.__get_cleaned_lastname(first_author)

                return shortname_format % (first_author_lastname, self.isbn)
        else:
            raise AttributeError()


class Part(model.CouchdbDocument):
    title = model.TextProperty(required=True)
    translated_titles = model.MultiCompositeTextProperty(subkeys=['title','language'])
    order = model.TextProperty(required=True)
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
