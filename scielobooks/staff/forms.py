from models import Monograph

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
    class Schema(colander.Schema):
        name = colander.SchemaNode(
            colander.String(),
            title='Publisher Name',
            description='Type the publisher name',
        )
        email = colander.SchemaNode(
            colander.String(),
            validator=colander.Email(),
            missing=None,
        )
        publisher_url = colander.SchemaNode(
            colander.String(),
            missing=None,
        )

    schema = Schema()

    @classmethod
    def get_form(cls):
        return deform.Form(cls.schema, buttons=('submit',))


class EvaluationForm():
    class Schema(colander.Schema):

        title = colander.SchemaNode(
            colander.String(),
        )
        isbn = colander.SchemaNode(
            colander.String(),
        )
        status = colander.SchemaNode(
            colander.String(),
            widget=deform.widget.SelectWidget(values=[('in_process','in process'),('approved','approved')],),
        )
        subject = colander.SchemaNode(
            colander.String(),
            widget=deform.widget.TextAreaWidget(),
            missing=None,
        )
        publisher_catalog_url = colander.SchemaNode(
            colander.String(),
            missing=None,
        )
        publisher = colander.SchemaNode(
            colander.String(),
            missing=None,
        )

    schema = Schema()

    @classmethod
    def get_form(cls):
        return deform.Form(cls.schema, buttons=('submit',))

class MeetingForm():
    class Schema(colander.Schema):
        date = colander.SchemaNode(
                colander.Date(),
                validator=colander.Range(
                    min=datetime.date.today(),
                    min_err='${val} is earlier than earliest date ${min}'
                    )
        )
        description = colander.SchemaNode(
            colander.String(),
            missing=None,
        )
    schema = Schema()

    @classmethod
    def get_form(cls):
        return deform.Form(cls.schema, buttons=('submit',))
