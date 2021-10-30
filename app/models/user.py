from flask_login import UserMixin
from flask import current_app as app
from app.utils import send_new_pass
from werkzeug.security import generate_password_hash, check_password_hash
import random
import string

# https://pynative.com/python-generate-random-string/#h-steps-to-create-a-random-string
def get_random_string(length=12):
    options = string.ascii_lowercase + string.digits
    result_str = ''.join(random.choice(options) for i in range(length))
    print("Random string of length", length, "is:", result_str)
    return result_str

from .. import login


class User(UserMixin):
    def __init__(self, id, email, firstname, lastname):
        self.id = id
        self.email = email
        self.firstname = firstname
        self.lastname = lastname

    @staticmethod
    def get_by_auth(email, password):
        rows = app.db.execute("""
SELECT password, id, email, firstname, lastname
FROM Users
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
FROM Users
WHERE email = :email
""",
                              email=email)
        return len(rows) > 0

    @staticmethod
    def register(email, password, firstname, lastname):
        try:
            rows = app.db.execute("""
INSERT INTO Users(email, password, firstname, lastname)
VALUES(:email, :password, :firstname, :lastname)
RETURNING id
""",
                                  email=email,
                                  password=generate_password_hash(password),
                                  firstname=firstname,
                                  lastname=lastname)
            id = rows[0][0]
            return User.get(id)
        except Exception as e:
            print(e)
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
    def get(id):
        rows = app.db.execute("""
SELECT id, email, firstname, lastname
FROM Users
WHERE id = :id
""",
                              id=id)
        return User(*(rows[0])) if rows else None
