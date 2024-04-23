#!/usr/bin/env python3
"""encrypt_password module."""
import bcrypt


def hash_password(password: str) -> bytes:
    """
    Hashes a password using bcrypt.

    Args:
    password (str): The password to hash.

    Returns:
    bytes: The salted, hashed password.
    """
    # Generate a salted, hashed password
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode(), salt)

    return hashed_password


def is_valid(hashed_password: bytes, password: str) -> bool:
    """
    Validates a password against its hashed counterpart using bcrypt.

    Args:
    hashed_password (bytes): The hashed password to compare.
    password (str): The password to validate.

    Returns:
    bool: True if the password matches the hashed password, False otherwise.
    """
    # Use bcrypt to validate the password
    return bcrypt.checkpw(password.encode(), hashed_password)
