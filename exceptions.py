# define Python user-defined exceptions


class UserNotFoundException(Exception):
    """Raised when user not found"""

    pass


class PasscodeAlreadySetException(Exception):
    """Raised when passcode is already set"""

    pass


class PhoneEmailVerificationPendingException(Exception):
    """Raised when phone email verification pending"""

    pass


class FailedPhoneOTPException(Exception):
    """Raised when failed to send phone otp"""

    pass


class NoCredentialsError(Exception):
    """Credentials not found"""

    pass


class NoBase64ImageFound(Exception):
    """Give Image is not base64"""

    pass


class WrongImageUrlException(Exception):
    """Unable to open file from given URL, Url may not contain image file"""

    pass
