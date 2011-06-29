from pyramid_mailer.message import Message
from sqlalchemy.orm.exc import NoResultFound
import models
import transaction
from datetime import datetime

class InvalidActivationKey(Exception):
    def __init__(self, message=None):
        super(Exception, self).__init__(message)

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.message)

class ActivationError(Exception):
    def __init__(self, message=None):
        super(Exception, self).__init__(message)

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.message)

class RegistrationProfileManager(object):

    @staticmethod
    def activate_user(activation_key, request):
        if activation_key == 'ACTIVATED':
            raise InvalidActivationKey()
            
        try:
            reg_profile = request.rel_db_session.query(models.RegistrationProfile).filter_by(activation_key=activation_key).one()
        except NoResultFound:
            raise InvalidActivationKey()

        if datetime.now() > reg_profile.expiration_date:
            raise InvalidActivationKey()

        reg_profile.user.is_active = True
        reg_profile.activation_key = 'ACTIVATED'
        reg_profile.activation_date = datetime.now()

        request.rel_db_session.add(reg_profile)
        try:
            request.rel_db_session.commit()
        except IntegrityError:
            request.rel_db_session.rollback()
            raise ActivationError()
        
        return reg_profile.user
    
    @staticmethod
    def send_activation_mail(user, request):
        if user.registration_profile.activation_key == 'ACTIVATED':
            raise InvalidActivationKey()

        activation_url = request.route_url('users.activation') + '?key=%s' % user.registration_profile.activation_key

        message = Message(subject="account activation",
                  sender=request.registry.settings['mail.default_sender'],
                  recipients=[user.email],
                  body="Hello %s, to activate your account please visit %s" % (user.username, activation_url))
        request.registry['mailer'].send(message)
        transaction.commit()

    @staticmethod
    def clean_expired(request):
        pass
