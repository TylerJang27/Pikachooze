from sqlalchemy import Column, Integer, String, Boolean, Sequence, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base


class Trainer(Base): 
    __tablename__ = 'trainer'

    trainer_seq = Sequence('trainer_seq', start=100)

    trainer_id = Column(Integer, trainer_seq, server_default=trainer_seq.next_value(), primary_key = True) 
    is_user = Column(Boolean)
    name = Column(String(40))
    pic = Column(String)
    game_id = Column(Integer, ForeignKey('game.game_id'))
    location_id = Column(Integer, ForeignKey('location.location_id'), nullable=True)
    added_by_id = Column(Integer, ForeignKey('users.uid'), nullable=True)

    game = relationship("Game") # no back populates unless strictly necessary
    location = relationship("Location")
    added_by = relationship("User", back_populates="trainers")
    trainer_pokemon = relationship("TrainerPokemon", back_populates="trainer")


    def __repr__(self):
        return "<Trainer(trainer_id='%d', name='%s', location_id='%d', added_by='%s')>" % (
                             self.trainer_id, self.name, (self.location_id if self.location_id else -1), (self.added_by.username if self.added_by is not None else "None"))