from pyramid_mailer.message import Message
from sqlalchemy.orm.exc import NoResultFound
import models
import transaction
from datetime import datetime
from Crypto.Hash import SHA256

ACTIVATED = 'ACTIVATED'
RECOVERED = 'RECOVERED'

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
        if activation_key == ACTIVATED:
            raise InvalidActivationKey()
            
        try:
            reg_profile = request.rel_db_session.query(models.RegistrationProfile).filter_by(activation_key=activation_key).one()
        except NoResultFound:
            raise InvalidActivationKey()

        if datetime.now() > reg_profile.expiration_date:
            raise InvalidActivationKey()

        reg_profile.user.is_active = True
        reg_profile.activation_key = ACTIVATED
        reg_profile.activation_date = datetime.now()

        request.rel_db_session.add(reg_profile)
        try:
            request.rel_db_session.commit()
        except IntegrityError:
            request.rel_db_session.rollback()
            raise ActivationError()
        
        return reg_profile.user
    
    @staticmethod
    def send_activation_mail(user, request, message=None):
        if user.registration_profile.activation_key == ACTIVATED:
            raise InvalidActivationKey()

        activation_url = request.route_url('users.activation') + '?key=%s' % user.registration_profile.activation_key        
        if message is None:
            message = "Hello %s, to activate your account please visit %s" % (user.username, activation_url)

        message = Message(subject="account activation",
                  sender=request.registry.settings['mail.default_sender'],
                  recipients=[user.email],
                  body=message)
        request.registry['mailer'].send(message)
        transaction.commit()

    @staticmethod
    def clean_expired(request):
        try:        
            exclude_total = request.rel_db_session.query(models.RegistrationProfile).filter(models.RegistrationProfile.activation_key != ACTIVATED and models.RegistrationProfile.expiration_date < datetime.now()).delete()
        except:
            pass
        
        return exclude_total


class AccountRecoveryManager(object):
    @staticmethod
    def redefine_password(recovery_key, new_password, request):
        if recovery_key == RECOVERED:
            raise InvalidActivationKey()
            
        try:
            account = request.rel_db_session.query(models.AccountRecovery).filter_by(recovery_key=recovery_key).one()
        except NoResultFound:
            raise InvalidActivationKey()

        if datetime.now() > account.expiration_date:
            raise InvalidActivationKey()

        account.user.password = SHA256.new(new_password).hexdigest()
        account.user.password_encryption = 'SHA256'
        account.recovery_key = RECOVERED
        account.recovery_date = datetime.now()

        request.rel_db_session.add(account)
        try:
            request.rel_db_session.commit()
        except IntegrityError:
            request.rel_db_session.rollback()
            raise ActivationError()
        
        return account.user

    @staticmethod
    def send_recovery_mail(user, request, message=None):
        if user.account_recovery[-1].recovery_key == RECOVERED:
            raise InvalidActivationKey()

        recovery_url = request.route_url('users.recover_password') + '?key=%s' % user.account_recovery[-1].recovery_key
        if message is None:
            message = "Hello %s, to recover your account please visit %s" % (user.username, recovery_url)

        message = Message(subject="account recovery",
                  sender=request.registry.settings['mail.default_sender'],
                  recipients=[user.email],
                  body=message)
        request.registry['mailer'].send(message)
        transaction.commit()
    
    @staticmethod
    def clean_expired(request):
        pass