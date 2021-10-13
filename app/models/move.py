from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base


class Move(Base):
    __tablename__ = 'move'

    move_id = Column(Integer, primary_key = True)
    move_name = Column(String(20), nullable=False)
    # target = Column(Enum, default=False) #TODO: ADD TARGET ENUM
    move_type_id = Column(Integer, ForeignKey('type.type_id'), nullable=False)
    base_damage = Column(Integer)
    base_accuracy = Column(Float)
    turn_takes = Column(Integer, default=1)
    pp = Column(Integer)

    move_type = relationship("Type")

    def __repr__(self):
        return "<Move(move_id='%d', move_name='%s', move_type='%s')>" % (
                             self.move_id, self.move_name, self.move_type.move_name)