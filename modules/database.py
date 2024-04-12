""" 
# --------------------------------------------------------------------------
# Data
# --------------------------------------------------------------------------
# Create a "database" to hold your data. This is just for example purposes. In
# a real world scenario you would likely connect to a SQL or NoSQL database.
"""

from passlib.handlers.sha2_crypt import sha512_crypt as crypto
from modules.model import Data, User


class DataBase:
    def __init__(self, email="user1@gmail.com", username="user1", password="12345"):
        # Init Database
        self.database = Data(
            user=[
                User(
                    email=email,
                    username=username,
                    hashed_password=crypto.hash(password),
                )
            ]
        )

    def db(self):
        return self.database

    def get_user(self, email: str) -> User:
        """Return user if exists

        Args:
            email (str): email for user

        Returns:
            User: User data
        """
        user = [user for user in self.database.user if user.email == email]
        if user:
            return user[0]
        return None
