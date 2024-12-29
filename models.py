from sqlalchemy import Column, Integer, String
from database import Base

class User(Base):
    __tablename__ = "User"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)

class SaveGame(Base):
    __tablename__ = 'savegame'

    id = Column(Integer, primary_key=True, index=True)
    player_usernames = Column(String, nullable=False)

    current_card_color = Column(String, nullable=False)
    current_card_type = Column(String, nullable=False)

    player1_hand = Column(String, nullable=False)
    player2_hand = Column(String, nullable=False)
    player3_hand = Column(String, nullable=False)
    player4_hand = Column(String, nullable=False)
