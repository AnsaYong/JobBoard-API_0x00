import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def is_valid_email(email):
    """
    Checks whether the given email is a valid email format.

    :param email: The email address to check.
    :return: (Boolean, String) - True if valid, False and error message otherwise.
    """

    if "@" not in email or email.count("@") != 1:
        return False, "Invalid email format: Must contain exactly one '@' symbol."

    local_part, domain_part = email.split("@", 1)

    # Local part validation (before @)
    if not re.match(r"^[a-zA-Z0-9._%+-]+$", local_part):
        return False, "Invalid email format: Local part contains invalid characters."

    # Domain validation (after @)
    if "." not in domain_part:
        return False, "Invalid email format: Domain must contain at least one '.'"

    if domain_part.startswith(".") or domain_part.endswith("."):
        return False, "Invalid email format: Domain cannot start or end with a dot."

    if ".." in domain_part:
        return False, "Invalid email format: Domain cannot contain consecutive dots."

    if not re.match(r"^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", domain_part):
        return False, "Invalid email format: Invalid domain structure."

    return True, ""


def validate_password(password):
    """
    Validates the password for a new user registration. The password must:
    - Be at least 8 characters long
    - Contain at least one letter
    - Contain at least one number
    - Contain at least one special character

    :param password: The user's password.
    :raises ValidationError: If the password is invalid.
    """
    if len(password) < 8:
        raise ValidationError(_("Password must be at least 8 characters long."))
    if not re.search(r"[A-Za-z]", password):
        raise ValidationError(_("Password must contain at least one letter."))
    if not re.search(r"\d", password):
        raise ValidationError(_("Password must contain at least one number."))
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise ValidationError(
            _("Password must contain at least one special character.")
        )
