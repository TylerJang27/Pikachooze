from sqlalchemy import Column, Integer, DateTime, Sequence, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base



class Purchase(Base):
    __tablename__ = 'purchases'

    id = Column(Integer, primary_key = True) #Sequence('purchase_id_seq'), 
    uid = Column(Integer, ForeignKey('users.id'))
    pid = Column(Integer, ForeignKey('products.id'))

    user = relationship("User", back_populates="purchases")
    product = relationship("Product", back_populates="purchases")

    time_purchased = Column(DateTime)

    def __repr__(self):
        return "<Purchase(id='%d', user='%s', product='%s', time_purchased='%s')>" % (
                             self.id, self.user.firstname, self.product.name, self.time_purchased)

"""
    def __init__(self, id, uid, pid, time_purchased):
        self.id = id
        self.uid = uid
        self.pid = pid
        self.time_purchased = time_purchased

    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT id, uid, pid, time_purchased
FROM Purchases
WHERE id = :id
''',
                              id=id)
        return Purchase(*(rows[0])) if rows else None

    @staticmethod
    def get_all_by_uid_since(uid, since):
        rows = app.db.execute('''
SELECT id, uid, pid, time_purchased
FROM Purchases
WHERE uid = :uid
AND time_purchased >= :since
ORDER BY time_purchased DESC
''',
                              uid=uid,
                              since=since)
        return [Purchase(*row) for row in rows]
"""