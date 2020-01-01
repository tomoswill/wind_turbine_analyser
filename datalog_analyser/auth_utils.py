from binascii import hexlify
from hashlib import pbkdf2_hmac, sha256
from os import urandom


def hash_password(password):
    """Hash a password for storing."""
    salt = sha256(urandom(60)).hexdigest().encode('ascii')
    pwdhash = hexlify(
        pbkdf2_hmac('sha512', password.encode('utf-8'), salt, 100000)
    )
    return (salt + pwdhash).decode('ascii')


def verify_password(stored_password, provided_password):
    """Verify a stored password against one provided by user"""
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    pwdhash = hexlify(
        pbkdf2_hmac('sha512', provided_password.encode('utf-8'), salt.encode('ascii'), 100000)
    ).decode('ascii')
    return pwdhash == stored_password
