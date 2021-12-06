from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.models.base import Base
import enum

class Target(enum.Enum):
    user = 1
    selected_pokemon = 2 
    ally = 3
    all_other_pokemon = 4
    random_opponent = 5
    all_opponents = 6
    users_field = 7
    specific_move = 8
    entire_field = 9
    opponents_field = 10
    user_and_allies = 11
    user_or_ally = 12
    all_pokemon = 13
    selected_pokemon_me_first = 14

class DamageClass(enum.Enum):
    physical = 1
    special = 2
    status = 3

class Move(Base):
    __tablename__ = 'move'

    move_id = Column(Integer, primary_key = True)
    move_name = Column(String(20), nullable=False)
    # target = Column(String(16), nullable=True)
    target = Column(Enum(Target), nullable=False)
    move_type_id = Column(Integer, ForeignKey('type.type_id'), nullable=False)
    power = Column(Integer, nullable=True)
    accuracy = Column(Integer, nullable=True)
    crit_rate = Column(Integer, nullable=True)
    # damage_class = Column(String, nullable=True)
    damage_class = Column(Enum(DamageClass), nullable=False)
    min_hits = Column(Integer, nullable=True)
    max_hits = Column(Integer, nullable=True)
    priority = Column(Integer, default=0)
    pp = Column(Integer, nullable=True)

    move_type = relationship("Type")

    def __repr__(self):
        return "<Move(move_id='%d', move_name='%s', move_type='%s')>" % (
                             self.move_id, self.move_name, self.move_type.move_name)