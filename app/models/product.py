from sqlalchemy import Column, Integer, Float, String, Boolean, Sequence
from sqlalchemy.orm import relationship
from app.models.base import Base

class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key = True) #Sequence('product_id_seq'),  
    name = Column(String)
    price = Column(Float)
    available = Column(Boolean)

    purchases = relationship("Purchase", back_populates="product")

    def __repr__(self):
        return "<Product(id='%d', name='%s', pid='%f', available='%b')>" % (
                             self.id, self.name, self.price, self.available)
"""
    def __init__(self, id, name, price, available):
        self.id = id
        self.name = name
        self.price = price
        self.available = available

    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT id, name, price, available
FROM Products
WHERE id = :id
''',
                              id=id)
        return Product(*(rows[0])) if rows is not None else None

    @staticmethod
    def get_all(available=True):
        rows = app.db.execute('''
SELECT id, name, price, available
FROM Products
WHERE available = :available
''',
                              available=available)
        return [Product(*row) for row in rows]
"""