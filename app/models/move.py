from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.models.base import Base
import enum

class Target(enum.Enum):
    user = 1
    selected_pokemon = 2 # note the underscore
    ally = 3
    all_other_pokemon = 4
    # TODO: ADD MORE AS NEEDED

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
    turn_takes = Column(Integer, default=1)
    priority = Column(Integer, default=0)
    pp = Column(Integer, nullable=True)

    move_type = relationship("Type")

    def __repr__(self):
        return "<Move(move_id='%d', move_name='%s', move_type='%s')>" % (
                             self.move_id, self.move_name, self.move_type.move_name)