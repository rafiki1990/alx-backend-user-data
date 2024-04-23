#!/usr/bin/env python3
"""Define _hash_password method."""
import bcrypt
from db import DB
from user import User
from sqlalchemy.orm.exc import NoResultFound
from typing import (TypeVar, Union)
import uuid


def _hash_password(password: str) -> bytes:
    """Hashes the input password using bcrypt.hashpw

    Args:
        password (str): The input password string to be hashed.

    Returns:
        bytes: The salted hash of the input password.
    """
    # Generate a salt using bcrypt.gensalt()
    salt = bcrypt.gensalt()

    # Hash the input password with the generated salt using bcrypt.hashpw()
    hashed_password = bcrypt.hashpw(password.encode(), salt)

    # Return the salted hash of the input password
    return hashed_password


def _generate_uuid() -> str:
    """Generate a new UUID

    Returns:
        str: A string representation of the generated UUID.
    """
    return str(uuid.uuid4())


class Auth:
    """Auth class to interact with the authentication database.
    """

    def __init__(self):
        self._db = DB()

    def register_user(self, email: str, password: str) -> User:
        """Register a new user

        Args:
            email (str): The email of the user to register.
            password (str): The password of the user to register.

        Returns:
            User: The newly registered User object.

        Raises:
            ValueError: If a user already exists with the provided email.
        """
        try:
            self._db.find_user_by(email=email)
        except NoResultFound:
            hashed = _hash_password(password)
            new_user = self._db.add_user(email, hashed)
            return new_user
        raise ValueError(f"User {email} already exists")

    def valid_login(self, email: str, password: str) -> bool:
        """Check if the login credentials are valid

        Args:
            email (str): The email of the user attempting to log in.
            password (str): The password of the user attempting to log in.

        Returns:
            bool: True if the login credentials are valid, False otherwise.
        """
        try:
            user = self._db.find_user_by(email=email)
        except NoResultFound:
            return False

        user_password = user.hashed_password
        passwd = password.encode("utf-8")
        return bcrypt.checkpw(passwd, user_password)

    def create_session(self, email: str) -> str:
        """Create a session for the user and return the session ID

        Args:
            email (str): The email of the user for whom the session is created.

        Returns:
            str: The session ID.
        """
        try:
            user = self._db.find_user_by(email=email)
            session_id = _generate_uuid()
            user.session_id = session_id
            self._db._session.commit()
            return session_id
        except NoResultFound:
            return None

    def get_user_from_session_id(self, session_id: str) -> User:
        """Get the user corresponding to the session ID

        Args:
            session_id (str): The session ID of the user.

        Returns:
            User: The corresponding user if found, else None.
        """
        if session_id is None:
            return None
        else:
            try:
                return self._db.find_user_by(session_id=session_id)
            except NoResultFound:
                return None

    def destroy_session(self, user_id: int) -> None:
        """Destroy the session for the user with the given user_id

        Args:
            user_id (int): The user ID of the user.

        Returns:
            None
        """
        self._db.update_user(user_id, session_id=None)

    def get_reset_password_token(self, email: str) -> str:
        """Generate and return a reset password token for the
        user with the given email.

        Args:
            email (str): The email of the user.

        Returns:
            str: The reset password token.

        Raises:
            ValueError: If no user is found with the given email.
        """
        # Find user corresponding to the email
        user = self._db.find_user_by(email=email)
        if not user:
            raise ValueError(f"No user found with email: {email}")

        # Generate a UUID for the reset password token
        reset_token = str(uuid.uuid4())

        # Update the user's reset_token database field
        self._db.update_user(user.id, reset_token=reset_token)

        return reset_token

    def update_password(self, reset_token: str, new_password: str) -> None:
        """Update the password of the user corresponding to the reset token.

        Args:
            reset_token (str): The reset token for the user.
            new_password (str): The new password for the user.

        Raises:
            ValueError: If no user is found with the given reset token.
        """
        # Find user corresponding to the reset token
        user = self._db.find_user_by(reset_token=reset_token)
        if not user:
            raise ValueError("No user found with the given reset token")

        # Hash the new password
        hashed_password = bcrypt.hashpw(
            new_password.encode(),
            bcrypt.gensalt()
            )

        # Update the user's hashed_password and reset_token fields
        self._db.update_user(
            user.id,
            hashed_password=hashed_password,
            reset_token=None
            )
