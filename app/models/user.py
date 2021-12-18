from flask_login import UserMixin
from flask import current_app as app
from app.utils import send_new_pass
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, Integer, String, Sequence, DateTime
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, sessionmaker
from app.models.base import Base, login
from app.config import Config
import random
import string

import datetime

def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


class User(Base, UserMixin):
    __tablename__ = 'users'
    users_id_seq = Sequence('users_id_seq')
    uid = Column(Integer, users_id_seq, server_default=users_id_seq.next_value(), primary_key = True)
    username = Column(String(20), nullable=False)
    email = Column(String(50), nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_trainer = Column(String(40), nullable=True)

    trainers = relationship("Trainer", back_populates="added_by")


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
            return User.get(rows[0][1])
                # return session.query(User).filter(User.email == email, check_password_hash(User.password, password)).one_or_none()
            # return User(*(rows[0][1:]))

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
    def register(email, password, username, game):
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
            # TODO: ADD SEQUENCE TO AVOID CONCURRENT ISSUES OF TRAINER ID
            rows2 = app.db.execute("""
INSERT INTO trainer(trainer_id, is_user, name, game_id, added_by_id)
VALUES((SELECT COUNT(*) FROM trainer) + 1, true, :username, :game_id, :uid) RETURNING trainer_id
""",
                                  username=username, uid=uid, game_id=game)
            return User.get(uid)
        except Exception as e:

            print("Unknown error during registration", str(e))
            # likely email already in use; better error checking and
            # reporting needed
            return None

    @staticmethod
    def forgot(email):
        new_random = get_random_string()
        
        # TODO: UPDATE TABLE NAME TO USERS LOWERCASE
        rows = app.db.execute("""
SELECT id, email, firstname, lastname
FROM Users
WHERE email = :email
""",
                              email=email)
        if rows: # TODO: UPDATE TABLE NAME TO USERS LOWERCASE
            id = rows[0][0]
            app.db.execute_no_return("""
UPDATE Users
SET password=:password
WHERE email = :email
""",
                              email=email, password=generate_password_hash(new_random))
            send_new_pass(email, new_random)
            return rows.get(id)

    @staticmethod
    @login.user_loader
    def get(uid):
        engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, echo=True) #TODO: GET FROM OTHER ONE
        Session = sessionmaker(engine, expire_on_commit=False)
        session = Session()
        return session.query(User).filter(User.uid == uid).one_or_none()
#         rows = app.db.execute("""
# SELECT uid, email, username
# FROM users
# WHERE uid = :uid
# """, uid=uid)
#         return User(*(rows[0])) if rows else None
