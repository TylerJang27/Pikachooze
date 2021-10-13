from sqlalchemy import Column, Integer, String, Boolean, Sequence, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base


class Trainer(Base):
    __tablename__ = 'trainer'

    trainer_id_seq = Sequence('trainer_id_seq')

    trainer_id = Column(Integer, trainer_id_seq, server_default=trainer_id_seq.next_value(), primary_key = True)
    is_user = Column(Boolean)
    name = Column(String(20))
    pic = Column(String)
    game_id = Column(Integer)
    # game_id = Column(Integer, ForeignKey('game.game_id')) # TODO: UNCOMMENT
    generation_id = Column(Integer, ForeignKey('generation'), default=4)
    location_id = Column(Integer, nullable=True)
    # location_id = Column(Integer, ForeignKey('location.location_id'), nullable=True) # TODO: UNCOMMENT
    added_by_id = Column(Integer, ForeignKey('users.uid'), nullable=True)

    game = relationship("Game") # no back populates unless strictly necessary
    generation = relationship("Generation")
    # location = relationship("Location", back_populates="trainers")
    added_by = relationship("User", back_populates="trainers")


    def __repr__(self):
        return "<Trainer(trainer_id='%d', name='%s', location_id='%d', added_by='%s')>" % (
                             self.trainer_id, self.name, self.location_id, (self.added_by.name if self.added_by is not None else "None"))