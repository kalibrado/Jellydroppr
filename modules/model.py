""" 
# --------------------------------------------------------------------------
# Models
# --------------------------------------------------------------------------

"""

from typing import List
from pydantic import BaseModel


class User(BaseModel):
    """Models for user"""

    email: str
    hashed_password: str


class Data(BaseModel):
    """Models for database"""

    user: List[User]

