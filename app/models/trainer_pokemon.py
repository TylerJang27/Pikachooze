from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Enum, Sequence
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import Base
import enum
import uuid

class GenderClass(enum.Enum):
    male = 1
    female = 2

class TrainerPokemon(Base):
    __tablename__ = 'trainer_pokemon'

    uuid = Column(UUID(as_uuid=True), unique=True, index=True, default=uuid.uuid4)
    trainer_pokemon_seq = Sequence('trainer_pokemon_seq', start=200) # TODO: CHANGE NUMBER IF MORE TRAINER POKEMON ADDED
    tp_id = Column(Integer, trainer_pokemon_seq, server_default=trainer_pokemon_seq.next_value(), primary_key = True)
    trainer_id = Column(Integer, ForeignKey('trainer.trainer_id')) # TODO: ADD INDEXES
    poke_id = Column(Integer, ForeignKey('pokemon.poke_id'))
    nickname = Column(String(25))
    gender = Column(Enum(GenderClass), default=GenderClass.male, nullable=True)
    level = Column(Integer, default=50)
    inParty = Column(Boolean, default=False)
    move1_id = Column(Integer, ForeignKey('move.move_id'), nullable=True)
    move2_id = Column(Integer, ForeignKey('move.move_id'), nullable=True)
    move3_id = Column(Integer, ForeignKey('move.move_id'), nullable=True)
    move4_id = Column(Integer, ForeignKey('move.move_id'), nullable=True)

    custom_hp = Column(Integer, nullable=True)
    custom_attack_stat = Column(Integer, nullable=True)
    custom_defense_stat = Column(Integer, nullable=True)
    custom_special_attack_stat = Column(Integer, nullable=True)
    custom_special_defense_stat = Column(Integer, nullable=True)
    custom_speed = Column(Integer, nullable=True)

    trainer = relationship("Trainer", back_populates="trainer_pokemon")
    pokemon = relationship("Pokemon") # Can add back populates in Pokemon if needed
    move1 = relationship("Move", foreign_keys=[move1_id])
    move2 = relationship("Move", foreign_keys=[move2_id])
    move3 = relationship("Move", foreign_keys=[move3_id])
    move4 = relationship("Move", foreign_keys=[move4_id])

    def __repr__(self):
        return "<TrainerPokemon(trainer='%s', pokemon='%s', nickname='%s', inParty='%r', level='%d', hp='%r', attack='%r', defense='%r', sp_attack='%r', sp_defense='%r', speed='%r', move1='%s', move2='%s', move3='%s', move4='%s')>" % (
                             self.trainer.name, self.pokemon.name, self.nickname, self.inParty, self.level, self.custom_hp, self.custom_attack_stat, self.custom_defense_stat, self.custom_special_attack_stat, self.custom_special_defense_stat, self.custom_speed,
                             (self.move1.move_name if self.move1 is not None else "None"),
                             (self.move2.move_name if self.move2 is not None else "None"),
                             (self.move3.move_name if self.move3 is not None else "None"),
                             (self.move4.move_name if self.move4 is not None else "None"))