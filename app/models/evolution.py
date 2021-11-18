from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base



class Evolution(Base):
    __tablename__ = 'evolution'

    poke1_id = Column(Integer, ForeignKey('pokemon.poke_id'), primary_key =True, nullable = False)
    poke2_id = Column(Integer, ForeignKey('pokemon.poke_id'), primary_key = True, nullable = False)
  
    poke1 = relationship("Pokemon", foreign_keys=[poke1_id]) 
    poke2 = relationship("Pokemon", foreign_keys=[poke2_id])

    def __repr__(self):
        return "<Evolution(poke1_id='%d', poke2_id='%d')>" % (
                             self.poke1_id, self.poke2_id)