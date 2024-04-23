#!/usr/bin/env python3
"""DB module
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import InvalidRequestError

from user import Base, User


class DB:
    """DB class
    """

    def __init__(self) -> None:
        """Initialize a new DB instance
        """
        self._engine = create_engine("sqlite:///a.db", echo=True)
        Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)
        self.__session = None

    @property
    def _session(self) -> Session:
        """Memoized session object
        """
        if self.__session is None:
            DBSession = sessionmaker(bind=self._engine)
            self.__session = DBSession()
        return self.__session

    def add_user(self, email: str, hashed_password: str) -> User:
        """Add a new user to the db

        Args:
            email (str): The email of the user.
            hashed_password (str): The hashed password of the user.

        Returns:
            User: The newly created User object.
        """
        user = User(email=email, hashed_password=hashed_password)
        self._session.add(user)
        self._session.commit()
        return user

    def find_user_by(self, **kwargs) -> User:
        """Find a user in the database based on input arguments

        Args:
            **kwargs: Arbitrary keyword arguments as filters for the query.

        Returns:
            User: The user found in the database.

        Raises:
            NoResultFound: If no result is found for the query.
            InvalidRequestError: If the query is invalid.
        """
        users = self._session.query(User)
        for key, value in kwargs.items():
            if key not in User.__dict__:
                raise InvalidRequestError
            for usr in users:
                if getattr(usr, key) == value:
                    return usr
        raise NoResultFound

    def update_user(self, user_id: int, **kwargs) -> None:
        """Update a user in the database based on input arguments

        Args:
            user_id (int): The ID of the user to update.
            **kwargs: Arbitrary keyword arguments as
                        updates for the user attributes.

        Raises:
            ValueError: If an argument that does not correspond to a
                        user attribute is passed.
        """
        try:
            user = self.find_user_by(id=user_id)
            for attr, value in kwargs.items():
                if hasattr(User, attr):
                    setattr(user, attr, value)
                else:
                    raise ValueError(f"Invalid attribute '{attr}' for user.")
            self._session.commit()
        except NoResultFound:
            raise NoResultFound(f"No user found with ID {user_id}.")
