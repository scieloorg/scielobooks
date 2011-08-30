from models import Monograph

from pyramid.i18n import TranslationStringFactory
_ = TranslationStringFactory('scielobooks')

import datetime
import deform
import colander
from ..utilities import functions

class MonographForm():

    @classmethod
    def get_form(cls, localizer):
        role_values = [('author','Author'),('translator','Translator'),('editor','Editor')]

        base_schema = Monograph.get_schema()
        base_schema['synopsis'].widget = deform.widget.TextAreaWidget(cols=80, rows=15)
        base_schema['creators'].children[0].children[0].widget = deform.widget.SelectWidget(values=role_values)

        #i18n
        base_schema.add(colander.SchemaNode(
            colander.String(),
            widget = deform.widget.HiddenWidget(),
            default= localizer.locale_name,
            name= '__LOCALE__',
        ))
        base_schema['title'].title = localizer.translate(_('Title'))
        base_schema['title'].description = localizer.translate(_('Title'))
        base_schema['isbn'].title = localizer.translate(_('ISBN'))
        base_schema['isbn'].description = localizer.translate(_('ISBN 13'))
        base_schema['creators'].title = localizer.translate(_('Creators'))
        base_schema['creators'].description = localizer.translate(_('Authors, translators, editors...'))
        base_schema['publisher'].title = localizer.translate(_('Publisher'))
        base_schema['publisher'].description = localizer.translate(_('Select the publisher'))
        base_schema['publisher_url'].title = localizer.translate(_('Publisher\'s Catalog URL'))
        base_schema['publisher_url'].description = localizer.translate(_('URL to the refered book, at the publisher\'s catalog'))
        base_schema['language'].title = localizer.translate(_('Language'))
        base_schema['language'].description = localizer.translate(_('Book language'))
        base_schema['synopsis'].title = localizer.translate(_('Synopsis'))
        base_schema['synopsis'].description = localizer.translate(_('Short synopsis'))
        base_schema['year'].title = localizer.translate(_('Year'))
        base_schema['year'].description = localizer.translate(_('Publication year'))
        base_schema['pages'].title = localizer.translate(_('Pages'))
        base_schema['pages'].description = localizer.translate(_('Number of pages'))
        base_schema['edition'].title = localizer.translate(_('Edition'))
        base_schema['edition'].description = localizer.translate(_('Edition'))
        base_schema['collection'].title = localizer.translate(_('Collection'))
        base_schema['collection'].description = localizer.translate(_('Collection'))
        base_schema['format'].title = localizer.translate(_('Format'))
        base_schema['format']['height'].title = localizer.translate(_('Height'))
        base_schema['format']['width'].title = localizer.translate(_('Width'))
        base_schema['book'].title = localizer.translate(_('Book'))
        base_schema['book'].description = localizer.translate(_('Book'))
        base_schema['serie'].title = localizer.translate(_('Serie'))
        base_schema['serie'].description = localizer.translate(_('serie'))
        base_schema['pdf_file'].title = localizer.translate(_('Book in PDF'))
        base_schema['pdf_file'].description = localizer.translate(_('Full book PDF'))
        base_schema['cover'].title = localizer.translate(_('Book Cover'))
        base_schema['cover'].description = localizer.translate(_('Book cover in high resolution'))
        base_schema['toc'].title = localizer.translate(_('Table of Contents'))
        base_schema['toc'].description = localizer.translate(_('TOC in PDF'))
        base_schema['editorial_decision'].title = localizer.translate(_('Editorial Decision'))
        base_schema['editorial_decision'].description = localizer.translate(_('Editorial Decision in PDF'))

        return deform.Form(base_schema, buttons=('submit',))


class PublisherForm():
    @classmethod
    def get_form(cls, localizer):
        class Schema(colander.Schema):
            name = colander.SchemaNode(
                colander.String(),
                title=localizer.translate(_('Publisher Name')),
                description=localizer.translate(_('Publisher name')),
            )
            email = colander.SchemaNode(
                colander.String(),
                validator=colander.Email(),
                missing=None,
                title=localizer.translate(_('E-mail')),
                description=localizer.translate(_('Contact e-mail')),
            )
            publisher_url = colander.SchemaNode(
                colander.String(),
                missing=None,
                title=localizer.translate(_('Institutional Site')),
                description=localizer.translate(_('URL to publisher\'s institutional site')),
            )
            __LOCALE__ = colander.SchemaNode(
                colander.String(),
                widget = deform.widget.HiddenWidget(),
                default= localizer.locale_name,
            )
        schema = Schema()

        return deform.Form(schema, buttons=('submit',))


class EvaluationForm():
    @classmethod
    def get_form(cls, localizer):
        class Schema(colander.Schema):
            title = colander.SchemaNode(
                colander.String(),
                title=localizer.translate(_('Book Title')),
                description=localizer.translate(_('Book title without abbreviations')),
            )
            isbn = colander.SchemaNode(
                colander.String(),
                title=localizer.translate(_('ISBN')),
                description=localizer.translate(_('ISBN 13')),
            )
            subject = colander.SchemaNode(
                colander.String(),
                widget=deform.widget.TextAreaWidget(),
                missing=None,
                title=localizer.translate(_('Subject')),
                description=localizer.translate(_('Subject key-words, separated by semi-colons ";"')),
            )
            publisher_catalog_url = colander.SchemaNode(
                colander.String(),
                missing=None,
                title=localizer.translate(_('Publisher\'s Catalog URL')),
                description=localizer.translate(_('URL to the refered book, at the publisher\'s catalog')),
            )
            publisher = colander.SchemaNode(
                colander.String(),
                missing=None,
                title=localizer.translate(_('Publisher')),
                description=localizer.translate(_('Publisher name')),
            )
            __LOCALE__ = colander.SchemaNode(
                colander.String(),
                widget = deform.widget.HiddenWidget(),
                default= localizer.locale_name,
            )
        schema = Schema()

        return deform.Form(schema, buttons=(localizer.translate(_('submit')),))

class MeetingForm():
    @classmethod
    def get_form(cls, localizer, default_css=None, **kwargs):
        class Schema(colander.Schema):
            date = colander.SchemaNode(
                    colander.Date(),
                    validator=colander.Range(
                        min=datetime.date.today(),
                        min_err='${val} is earlier than earliest date ${min}'
                        ),
                    title=localizer.translate(_('Meeting Date')),
                    description=localizer.translate(_('Select the meeting date')),
            )
            description = colander.SchemaNode(
                colander.String(),
                missing=None,
                title=localizer.translate(_('Description')),
                description=localizer.translate(_('Short description about the meeting')),
            )
            __LOCALE__ = colander.SchemaNode(
                colander.String(),
                widget = deform.widget.HiddenWidget(),
                default= localizer.locale_name,
            )
        schema = Schema()
        form = deform.Form(schema, buttons=('submit',))
        functions.customize_form_css_class(form, default_css, **kwargs)
        return form
