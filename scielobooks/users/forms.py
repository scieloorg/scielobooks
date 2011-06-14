from pyramid.i18n import TranslationStringFactory
_ = TranslationStringFactory('scielobooks')

import datetime
import deform
import colander

class SignupForm():
    @classmethod
    def get_form(cls, localizer, publishers):
        class Schema(colander.Schema):
            username = colander.SchemaNode(
                colander.String(),
                title=localizer.translate(_('Publisher Name')),
                description=localizer.translate(_('User name')),
            )
            password = colander.SchemaNode(
                colander.String(),
                validator=colander.Length(min=5),
                widget=deform.widget.CheckedPasswordWidget(size=20),
                description=localizer.translate(_('Type your password and confirm it')),
            )
            email = colander.SchemaNode(
                colander.String(),
                validator=colander.Email(),
                missing=None,
                title=localizer.translate(_('E-mail')),
                description=localizer.translate(_('Contact e-mail')),
            )
            email = colander.SchemaNode(
                colander.String(),
                validator=colander.Email(),
                widget=deform.widget.SelectWidget(values=publishers),
                title=localizer.translate(_('E-mail')),
                description=localizer.translate(_('Contact e-mail')),
            )
            __LOCALE__ = colander.SchemaNode(
                colander.String(),
                widget = deform.widget.HiddenWidget(),
                default= localizer.locale_name,
            )
        schema = Schema()

        return deform.Form(schema, buttons=('submit',))