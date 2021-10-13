from flask_login import UserMixin
from flask import current_app as app
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, Integer, String, Sequence, DateTime
from sqlalchemy.orm import relationship
from app.models.base import Base, login
import datetime


class User(Base, UserMixin):
    __tablename__ = 'users'

    users_id_seq = Sequence('users_id_seq')
    uid = Column(Integer, users_id_seq, server_default=users_id_seq.next_value(), primary_key = True)
    username = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    purchases = relationship("Purchase", back_populates="user")


    def __repr__(self):
        return "<User(uid='%d', username='%s', email='%s')>" % (
                             self.uid, self.username, self.email)

    def __init__(self, uid, email, username):
        self.uid = uid
        self.email = email
        self.username = username

    def get_id(self):
        return (self.uid)

    @staticmethod
    def get_by_auth(email, password):
        rows = app.db.execute("""
SELECT password, uid, username, email
FROM users
WHERE email = :email
""",
                              email=email)
        if not rows:  # email not found
            return None
        elif not check_password_hash(rows[0][0], password):
            # incorrect password
            return None
        else:
            return User(*(rows[0][1:]))

    @staticmethod
    def email_exists(email):
        rows = app.db.execute("""
SELECT email
FROM users
WHERE email = :email
""",
                              email=email)
        return len(rows) > 0

    @staticmethod
    def register(email, password, username):
        try:
            rows = app.db.execute("""
INSERT INTO Users(email, password, username)
VALUES(:email, :password, :username)
RETURNING uid
""",
                                  email=email,
                                  password=generate_password_hash(password),
                                  username=username)
            uid = rows[0][0]
            return User.get(uid)
        except Exception as e:

            print("Unknown error during registration", str(e))
            # likely email already in use; better error checking and
            # reporting needed
            return None

    @staticmethod
    @login.user_loader
    def get(uid):
        rows = app.db.execute("""
SELECT uid, email, username
FROM users
WHERE uid = :uid
""", uid=uid)
        return User(*(rows[0])) if rows else None
