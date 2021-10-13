from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base


# TODO: CAN EXTRACT INTO THE ASSOCIATION TABLE, SEE DOCS
class CanLearn(Base):
    __tablename__ = 'can_learn'

    poke_id = Column(Integer, ForeignKey('pokemon.poke_id'), primary_key = True)
    move_id = Column(Integer, ForeignKey('move.move_id'), primary_key = True)

    pokemon = relationship("Pokmemon", back_populates="learnable_moves")
    move = relationship("Move") # can add pokemon that can learn if necessary

    def __repr__(self):
        return "<CanLearn(pokemon='%s', move='%s')>" % (
                             self.pokemon.name, self.move.move_name)