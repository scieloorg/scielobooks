from models import Monograph

from pyramid.i18n import TranslationStringFactory
_ = TranslationStringFactory('scielobooks')

import datetime
import deform
import colander


class MonographForm():
    
    role_values = [('author','Author'),('translator','Translator'),('editor','Editor')]

    base_schema = Monograph.get_schema()
    base_schema['synopsis'].widget = deform.widget.TextAreaWidget(cols=80, rows=15)
    base_schema['creators'].children[0].children[0].widget = deform.widget.SelectWidget(values=role_values)

    @classmethod
    def get_form(cls):
        return deform.Form(cls.base_schema, buttons=('submit',))


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
            status = colander.SchemaNode(
                colander.String(),
                widget=deform.widget.SelectWidget(values=[('in_process','in process'),('approved','approved')],),
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
    def get_form(cls, localizer):
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

        return deform.Form(schema, buttons=('submit',))
