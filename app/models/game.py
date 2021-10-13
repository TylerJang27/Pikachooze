from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base


class Game(Base):
    __tablename__ = 'game'

    game_id = Column(Integer, primary_key = True)
    game_name = Column(String(16), index=True, unique=True)
    generation_id = Column(Integer, ForeignKey('generation'), default=4)

    generation = relationship("Generation", back_populates="games")

    def __repr__(self):
        return "<Game(game_id='%d', game_name='%s')>" % (
                             self.game_id, self.game_name)