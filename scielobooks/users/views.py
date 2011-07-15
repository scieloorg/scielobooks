# coding: utf-8

from pyramid.view import view_config
from pyramid.response import Response
from pyramid import exceptions
from pyramid.url import route_url, static_url
from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import get_renderer
from pyramid.security import remember, forget
from pyramid.security import authenticated_userid
from pyramid.i18n import get_localizer
from pyramid.i18n import TranslationStringFactory
_ = TranslationStringFactory('scielobooks')

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from datetime import date

from forms import SignupForm, LoginForm, RecoverPasswordForm, ForgotPasswordForm, EditUserForm
import models as users
from ..models import models
from managers import RegistrationProfileManager
from managers import InvalidActivationKey
from managers import ActivationError
from managers import AccountRecoveryManager

from Crypto.Hash import SHA256

import json
import deform
import colander
import base64

BASE_TEMPLATE = 'scielobooks:templates/base.pt'


def get_logged_user(request):
    userid = authenticated_userid(request)
    if userid:
        return request.rel_db_session.query(users.User).get(userid)


def login(request):
    FORM_TITLE = _('Login')
    localizer = get_localizer(request)
    main = get_renderer(BASE_TEMPLATE).implementation()
    login_form = LoginForm.get_form(localizer)

    login_url = route_url('users.login', request)
    referrer = request.url
    if referrer == login_url:
        referrer = route_url('staff.panel', request)

    b64_caller = request.params.get('caller', None)
    caller = base64.b64decode(b64_caller) if b64_caller is not None else referrer
    
    if request.method == 'POST':
        
        controls = request.POST.items()
        try:
            appstruct = login_form.validate(controls)
        except deform.ValidationFailure, e:
            
            return {'content':e.render(), 
                    'main':main, 
                    'form_stuff':{'form_title':FORM_TITLE},
                    'user':get_logged_user(request),
                    }
        try:
            user = request.rel_db_session.query(users.User).filter_by(username=appstruct['username']).one()
        except NoResultFound:
            request.session.flash(_("Username doesn't exist."))
        else:
            if SHA256.new(appstruct['password']).hexdigest() == user.password:
                if not user.is_active:
                    request.session.flash(_("The username is not active. Check your email account for the activation instructions."))
                else:
                    headers = remember(request, user.id)
                    return HTTPFound(location=caller, headers=headers)
            else:
                request.session.flash(_("Username/password doesn't match"))             

    return {
            'main':main,
            'content':login_form.render(),
            'form_stuff':{'form_title':FORM_TITLE},
            'user':get_logged_user(request),
           }


def logout(request):
    headers = forget(request)
    return HTTPFound(location = route_url('users.login', request),
                     headers = headers)


def signup(request):
    FORM_TITLE = _('Signup')
    localizer = get_localizer(request)
    main = get_renderer(BASE_TEMPLATE).implementation()
    publisher = request.rel_db_session.query(models.Publisher.name_slug, models.Publisher.name).all()
    signup_form = SignupForm.get_form(localizer,publisher)

    if request.method == 'POST':
                
        controls = request.POST.items()
        try:
            appstruct = signup_form.validate(controls)
        except deform.ValidationFailure, e:
            
            return {'content':e.render(), 
                    'main':main, 
                    'form_stuff':{'form_title':FORM_TITLE},
                    'user':get_logged_user(request),
                    }

        del(appstruct['__LOCALE__'])

        appstruct['publisher'] = request.rel_db_session.query(models.Publisher).filter_by(name_slug=appstruct['publisher']).one()
        
        #FIXME! so bizarre!
        try:
            group = request.rel_db_session.query(users.Group).filter_by(name=appstruct['group']).one()
        except NoResultFound:
            group = users.Group(name=appstruct['group'])
            request.rel_db_session.add(group)
            request.rel_db_session.commit()
        finally:
            group_name = appstruct['group']
            del(appstruct['group'])
     
        if group_name == 'editor':
            user = models.Editor(group=group,**appstruct)
        elif group_name == 'admin':
            del(appstruct['publisher'])
            user = models.Admin(group=group,**appstruct)
        
        registration_profile = users.RegistrationProfile(user)

        RegistrationProfileManager.clean_expired(request)

        request.rel_db_session.add(user)
        request.rel_db_session.add(registration_profile)

        try:
            request.rel_db_session.commit()
        except IntegrityError:
            request.rel_db_session.rollback()
            request.session.flash(_('This username already exists.'))
            return {'content':signup_form.render(appstruct),
                    'main':main,
                    'form_stuff':{'form_title':FORM_TITLE},
                    'user':get_logged_user(request),
                    }
        else:            
            RegistrationProfileManager.send_activation_mail(user, request)


        request.session.flash(_('Successfully added.'))
        return HTTPFound(location=request.route_path('staff.panel'))

    return {'content':signup_form.render(),
            'form_stuff':{'form_title':FORM_TITLE},
            'main':main,
            'user':get_logged_user(request),
            }

def activation(request):
    main = get_renderer(BASE_TEMPLATE).implementation()

    activation_key = request.params.get('key', None)
    if activation_key is None:
        raise exceptions.NotFound()
    
    try:
        user = RegistrationProfileManager.activate_user(activation_key, request)
    except InvalidActivationKey:
        raise exceptions.NotFound()
    except ActivationError:
        request.session.flash(_('Problems occured when trying to activate the user. Please try again.'))
        return {'main':main, 'active':False}

    request.session.flash(_('User %s has been activated successfuly.' % user.username))

    return {'main':main, 'active':True}

def forgot_password(request):
    FORM_TITLE = _('Password Recovery')
    main = get_renderer(BASE_TEMPLATE).implementation()
    localizer = get_localizer(request)
    forgot_password_form = ForgotPasswordForm.get_form(localizer)

    if request.method == 'POST':
        controls = request.POST.items()
        try:
            appstruct = forgot_password_form.validate(controls)
        except deform.ValidationFailure, e:            
            return {'content':e.render(), 
                    'main':main, 
                    'form_stuff':{'form_title':FORM_TITLE},
                    'user':get_logged_user(request),
                    }

        del(appstruct['__LOCALE__'])
        try:
            user = request.rel_db_session.query(users.User).filter_by(username=appstruct['username']).one()
        except NoResultFound:
            request.session.flash(_("Username doesn't exist."))
            return {'content':forgot_password_form.render(appstruct),
                    'main':main,
                    'form_stuff':{'form_title':FORM_TITLE},
                    'user':get_logged_user(request),
                    }
        
        account = users.AccountRecovery(user)
        request.rel_db_session.add(account)

        try:
            request.rel_db_session.commit()
        except:
            request.rel_db_session.rollback()
            request.session.flash(_('Problems occured when trying to redefine the user password. Please try again.'))
            return {'content':forgot_password_form.render(appstruct),
                    'main':main,
                    'form_stuff':{'form_title':FORM_TITLE},
                    'user':get_logged_user(request),
                    }
        else:
            AccountRecoveryManager.send_recovery_mail(user, request)

        request.session.flash(_('You will receive an email with instructions on how to reset your account password.'))
        return HTTPFound(location=request.route_path('users.forgot_password'))

    return {'content':forgot_password_form.render(),
            'main':main,
            'form_stuff':{'form_title':FORM_TITLE},
            'user':get_logged_user(request),
            }

def recover_password(request):
    FORM_TITLE = _('Password Recovery')
    main = get_renderer(BASE_TEMPLATE).implementation()
    localizer = get_localizer(request)
    recovery_form = RecoverPasswordForm.get_form(localizer)

    recovery_key = request.params.get('key', None)
    if recovery_key is None:
        raise exceptions.NotFound()
    
    if request.method == 'POST':
        controls = request.POST.items()
        try:
            appstruct = recovery_form.validate(controls)
        except deform.ValidationFailure, e:            
            return {'content':e.render(), 
                    'main':main, 
                    'form_stuff':{'form_title':FORM_TITLE},
                    'user':get_logged_user(request),
                    }

        del(appstruct['__LOCALE__'])
        try:
            user = AccountRecoveryManager.redefine_password(appstruct['recovery_key'], appstruct['new_password'], request)
            request.session.flash(_('Password successfully redefined.'))
        except InvalidActivationKey:
            raise exceptions.NotFound()
        except ActivationError:
            request.session.flash(_('Problems occured when trying to redefine the user password. Please try again.'))

        return HTTPFound(location=request.route_path('users.login'))
    else:
        try:
            account = request.rel_db_session.query(users.AccountRecovery).filter_by(recovery_key=recovery_key).one()
        except NoResultFound:
            raise exceptions.NotFound()
        
    return {'content':recovery_form.render({'recovery_key':recovery_key}),
            'main':main, 
            'form_stuff':{'form_title':FORM_TITLE},
            'user':get_logged_user(request),
            }

def users_list(request):
    main = get_renderer(BASE_TEMPLATE).implementation()    
    user_list = request.rel_db_session.query(users.User).all()

    return {'users':user_list,
            'main':main,
            'breadcrumb': {'home':request.route_path('staff.panel')},
            }

def edit_user(request):
    FORM_TITLE = _('Edit User')
    main = get_renderer(BASE_TEMPLATE).implementation()
    localizer = get_localizer(request)
    publishers = request.rel_db_session.query(models.Publisher.name_slug, models.Publisher.name).all()
    edit_user_form = EditUserForm.get_form(localizer,publishers)

    if request.method == 'POST':
        controls = request.POST.items()
        try:
            appstruct = edit_user_form.validate(controls)
        except deform.ValidationFailure, e:
            
            return {'content':e.render(), 
                    'main':main, 
                    'form_stuff':{'form_title':FORM_TITLE},
                    'user':get_logged_user(request),
                    }
        
        try:
            user = request.rel_db_session.query(users.User).filter_by(id=appstruct['_id']).one()
        except NoResultFound:
            raise exceptions.NotFound()
        
        if appstruct['password'] is not None:
            user.password = SHA256.new(appstruct['password']).hexdigest()
            user.password_encryption = 'SHA256'

        if len(appstruct['email']):
            user.email = appstruct['email']

        if appstruct['group'] != user.group.name:
            group = request.rel_db_session.query(users.Group).filter_by(name=appstruct['group']).one()
            user.group = group            

        request.rel_db_session.add(user)
        try:
            request.rel_db_session.commit()
        except:
            request.rel_db_session.rollback()
            request.session.flash(_('Problems occured when trying to update user data. Please try again.'))
        else:
            request.session.flash(_('Successfully updated.'))

        return HTTPFound(location=request.route_path('users.edit_user', id=user.id))

    if 'id' in request.matchdict:
        try:
            user = request.rel_db_session.query(users.User).filter_by(id=request.matchdict['id']).one()
        except NoResultFound:
            raise exceptions.NotFound()

        appstruct = {'email':user.email,
                     'group':user.group.name,
                     '_id':user.id}

        return {'content':edit_user_form.render(appstruct),
                'main':main,
                'form_stuff':{'form_title':FORM_TITLE},                
                'user':get_logged_user(request),
                }
    
    raise exceptions.NotFound()

def ajax_set_active(request):
    user_id = request.POST.get('id', None)
    if user_id is None:
        return Respose('insufficient params')
    
    try:
        user = request.rel_db_session.query(users.User).filter_by(id=user_id).one()
    except NoResultFound:
        return Respose('nothing to do')

    activation_key = user.registration_profile.activation_key
    
    try:
        user = RegistrationProfileManager.activate_user(activation_key, request)
    except InvalidActivationKey:
        if user.is_active == False:
            user.is_active = True
            request.rel_db_session.add(user)
            try:
                request.rel_db_session.commit()
            except:
                request.rel_db_session.rollback()
                return Response('error')

    except ActivationError:        
        return Response('error')
  
    return Response('done')

def ajax_set_inactive(request):
    user_id = request.POST.get('id', None)
    if user_id is None:
        return Respose('insufficient params')
    
    try:
        user = request.rel_db_session.query(users.User).filter_by(id=user_id).one()
    except NoResultFound:
        return Respose('nothing to do')

    if user.is_active == True:
        user.is_active = False
        request.rel_db_session.add(user)
        try:
            request.rel_db_session.commit()
        except:
            request.rel_db_session.rollback()
            return Response('error')

    return Response('done')