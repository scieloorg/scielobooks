from pyramid.i18n import TranslationStringFactory
_ = TranslationStringFactory('scielobooks')

import datetime
import deform
import colander

class SignupForm():
    @classmethod
    def get_form(cls, localizer, publishers):
        
        def validate_username(node, value):
            msg = _("Username must not contains non alphanumeric digits",)
            if not value.isalnum():
                raise colander.Invalid(node, msg)
            
        class Schema(colander.Schema):
            username = colander.SchemaNode(
                colander.String(),
                validator=colander.All(validate_username),
                title=localizer.translate(_('Username')),
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
            group = colander.SchemaNode(
                colander.String(),
                widget=deform.widget.SelectWidget(values=[('editor','Editor'),('admin','Administrator')]),
                title=localizer.translate(_('Group')),
                description=localizer.translate(_('Group name')),
            )
            publisher = colander.SchemaNode(
                colander.String(),
                widget=deform.widget.SelectWidget(values=publishers),
                title=localizer.translate(_('Publisher')),
                description=localizer.translate(_('Publisher name')),
            )
            __LOCALE__ = colander.SchemaNode(
                colander.String(),
                widget = deform.widget.HiddenWidget(),
                default= localizer.locale_name,
            )
        schema = Schema()

        return deform.Form(schema, buttons=('submit',))

class LoginForm():
    @classmethod
    def get_form(cls, localizer):
        
        class Schema(colander.Schema):
            username = colander.SchemaNode(
                colander.String(),
                title=localizer.translate(_('Username')),
                description=localizer.translate(_('User name')),
            )
            password = colander.SchemaNode(
                colander.String(),
                validator=colander.Length(min=5),
                widget=deform.widget.PasswordWidget(size=20),
                description=localizer.translate(_('Type your password and confirm it')),
            )
            __LOCALE__ = colander.SchemaNode(
                colander.String(),
                widget = deform.widget.HiddenWidget(),
                default= localizer.locale_name,
            )
        schema = Schema()

        return deform.Form(schema, buttons=('submit',))

class ForgotPasswordForm():
    @classmethod
    def get_form(cls, localizer):
        
        class Schema(colander.Schema):
            username = colander.SchemaNode(
                colander.String(),
                title=localizer.translate(_('Username')),
                description=localizer.translate(_('User name')),
            )            
            __LOCALE__ = colander.SchemaNode(
                colander.String(),
                widget = deform.widget.HiddenWidget(),
                default= localizer.locale_name,
            )
        schema = Schema()

        return deform.Form(schema, buttons=('submit',))

class RecoverPasswordForm():
    @classmethod
    def get_form(cls, localizer):
        
        class Schema(colander.Schema):
            new_password = colander.SchemaNode(
                colander.String(),
                validator=colander.Length(min=5),
                widget=deform.widget.CheckedPasswordWidget(size=20),
                description=localizer.translate(_('Type your password and confirm it')),
            )
            recovery_key = colander.SchemaNode(
                colander.String(),
                widget = deform.widget.HiddenWidget(),                
            )
            __LOCALE__ = colander.SchemaNode(
                colander.String(),
                widget = deform.widget.HiddenWidget(),
                default= localizer.locale_name,
            )
        schema = Schema()

        return deform.Form(schema, buttons=('submit',))