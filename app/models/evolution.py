from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base



class Evolution(Base):
    __tablename__ = 'evolution'

<<<<<<< HEAD
    poke1_id = Column(Integer, ForeignKey('pokemon.poke_id'), primary_key =True, nullabe = False)
    poke2_id = Column(Integer, ForeignKey('pokemon.poke_id'), primary_key = True, nullabe = False)
=======
    poke1_id = Column(Integer, ForeignKey('pokemon.poke_id'), primary_key =True, nullable = False)
    poke2_id = Column(Integer, ForeignKey('pokemon.poke_id'), primary_key = True, nullable = False)
>>>>>>> f622ded196590aad9261e2f655654b86e810822b
  
    poke1 = relationship("Pokemon", foreign_keys=[poke1_id]) 
    poke2 = relationship("Pokemon", foreign_keys=[poke2_id])

    def __repr__(self):
        return "<Evolution(poke1_id='%d', poke2_id='%d')>" % (
                             self.poke1_id, self.poke2_id)