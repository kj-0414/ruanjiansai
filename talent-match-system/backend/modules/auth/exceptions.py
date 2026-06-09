class AuthException(Exception):
    pass


class InvalidPhoneException(AuthException):
    pass


class InvalidCodeException(AuthException):
    pass


class PhoneAlreadyRegisteredException(AuthException):
    pass


class AuthenticationFailedException(AuthException):
    pass


class UserNotFoundException(AuthException):
    pass