from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base


class Game(Base):
    __tablename__ = 'game'

    game_id = Column(Integer, primary_key = True)
    game_name = Column(String(16), index=True, unique=True, nullable=False)
    generation_id = Column(Integer, ForeignKey('generation.generation'), default=4, nullable=False)

    generation = relationship("Generation", back_populates="games")
    locations = relationship("Location", back_populates="game")

    def __repr__(self):
        return "<Game(game_id='%d', game_name='%s')>" % (
                             self.game_id, self.game_name)