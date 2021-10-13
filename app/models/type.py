from sqlalchemy import Column, Integer, String
from app.models.base import Base


class Type(Base):
    __tablename__ = 'type'

    type_id = Column(Integer, primary_key = True)
    type_name = Column(String(16), index=True, unique=True)

    def __repr__(self):
        return "<Type(type_id='%d', type_name='%s')>" % (
                             self.type_id, self.type_name)