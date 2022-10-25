import bcrypt
import email_validator


def validate_password(password: str) -> str:
    if len(password) < 8:
        return "The password should be more than 8 characters"
    return ""


def validate_email(email: str) -> str:
    try:
        email_validator.validate_email(email=email, check_deliverability=False)
    except email_validator.EmailSyntaxError as err:
        return str(err)
    return ""


def password2hash(password: str) -> str:
    byte_password = password.encode()
    return bcrypt.hashpw(
        byte_password,
        bcrypt.gensalt(),
    ).decode()


def match_passwords(
    password: str,
    password_hashed: str,
) -> bool:
    byte_password = password.encode()
    byte_password_hashed = password_hashed.encode()

    return bcrypt.checkpw(
        byte_password,
        byte_password_hashed,
    )
