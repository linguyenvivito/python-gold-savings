from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String

from src.core.database import Base


class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String)
    password_hash = Column(String)

class Store(Base):

    __tablename__ = "stores"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    address = Column(String)
    phone = Column(String)
    culture = Column(String)
    note = Column(String)