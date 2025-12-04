"""
Authentication helpers for hashing and verifying passwords.
"""
from werkzeug.security import generate_password_hash, check_password_hash


def hash_password(plain_password: str) -> str:
    """
    Here we are returning a secure hash of the given plaintext password.
    """
    return generate_password_hash(plain_password)


def verify_password(plain_password: str, hashed: str) -> bool:
    """
    Here we are checking whether the plaintext password matches the stored hash.
    """
    return check_password_hash(hashed, plain_password)
