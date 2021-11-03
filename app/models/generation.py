from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.models.base import Base


class Generation(Base):
    __tablename__ = 'generation'

    generation = Column(Integer, primary_key = True)

    games = relationship("Game", back_populates="generation")

    def __repr__(self):
        return "<Generation(generation='%d')>" % (self.generation)