from sqlalchemy import Column, Integer, String
from database import Base

class User(Base):
    __tablename__ = "User"  # نام جدول در پایگاه داده

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
