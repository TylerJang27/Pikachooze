from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base


class PokemonBaseStats(Base):
    __tablename__ = 'pokemonbasestats'

    poke_id = Column(Integer, ForeignKey('pokemon.poke_id'), primary_key = True)
    hp = Column(Integer, nullable=False)
    speed = Column(Integer, nullable=True)
    attack_stat = Column(Integer, nullable=True)
    special_attack_stat = Column(Integer, nullable=True)
    defense_stat = Column(Integer, nullable=True)
    special_defense_stat = Column(Integer, nullable=True)
    #...

    pokemon = relationship("Pokmemon", back_populates="pokemon_base_stats")

    def __repr__(self):
        return "<PokemonBaseStats(poke_id='%d', hp='%d', speed='%d')>" % (
                             self.poke_id, self.hp, self.speed)