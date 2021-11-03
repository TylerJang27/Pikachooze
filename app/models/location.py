from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.models.base import Base


class Location(Base):
    __tablename__ = 'location'

    location_id = Column(Integer, primary_key = True)
    location_name = Column(String(25), nullable=False)
    is_route = Column(Boolean, default=False)
    is_gym = Column(Boolean, default=False)
    game_id = Column(Integer, ForeignKey('game.game_id'), nullable=False)

    game = relationship("Game", back_populates="locations")

    def __repr__(self):
        return "<Location(location_id='%d', location_name='%s', game='%s')>" % (
                             self.location_id, self.location_name, self.game.game_name)