import math
import re

from django.core.exceptions import ValidationError


def validate_length(value, length):
    return int(math.log10(value)) + 1 == length


def validate_pincode(value, length=6):

    if not validate_length(value, length):
        raise ValidationError(
            f'pin-code should be of {length=}'
        )


def validate_phone_no(value, length=10):

    if not validate_length(value, length):
        raise ValidationError(
            f'phone number should be of {length=}'
        )


def validate_email(email):
    # regular expression for validating an Email
    regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'
    return re.search(regex, email)


def validate_password(password):
    # regular expression for password
    # Min 8 length, Max 25 length
    # At least 1 uppercase
    # At least 1 lowercase

    reg = "^(?=.*[a-z])(?=.*[A-Z])[A-Za-z\d@$!#%*?&]{8,25}$"

    # searching regex
    mat = re.search(reg, password)

    # validating conditions
    if mat:
        return True

    return False
