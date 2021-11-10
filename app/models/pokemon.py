from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base


class Pokemon(Base):
    __tablename__ = 'pokemon'

    poke_id = Column(Integer, primary_key = True)
    name = Column(String(20))
    generation_id = Column(Integer, ForeignKey('generation.generation'), default=4)
    type1_id = Column(Integer, ForeignKey('type.type_id'), nullable=False)
    type2_id = Column(Integer, ForeignKey('type.type_id'), nullable=True)
    pic = Column(String(90), nullable=False)

    generation = relationship("Generation")
    type1 = relationship("Type", foreign_keys=[type1_id]) # Can add back populates in Type if needed
    type2 = relationship("Type", foreign_keys=[type2_id])
    pokemon_base_stats = relationship("PokemonBaseStats", back_populates="pokemon")
    learnable_moves = relationship("CanLearn", back_populates="pokemon")

    def __repr__(self):
        return "<Pokemon(poke_id='%d', name='%s', type1='%s', type2='%s')>" % (
                             self.poke_id, self.name, self.type1.type_name, (self.type2.type_name if self.type2 is not None else "None"))