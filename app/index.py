from flask import render_template
from flask_login import current_user
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import datetime

#from .models.product import Product
#from .models.purchase import Purchase
from sqlalchemy.orm import Session
from app.models.purchase import Purchase
from app.db import DB
from app.config import Config

from flask import Blueprint
bp = Blueprint('index', __name__)


@bp.route('/')
def index():

    '''
    # get all available products for sale:
    products = Product.get_all(True)
    # find the products current user has bought:
    if current_user.is_authenticated:
        purchases = Purchase.get_all_by_uid_since(
            current_user.id, datetime.datetime(1980, 9, 14, 0, 0, 0))
    else:
        purchases = None
    # render the page by adding information to the index.html file
    return render_template('index.html',
                           avail_products=products,
                           purchase_history=purchases)'''
    print("About to print purchases:")
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, echo=True) #TODO: GET FROM OTHER ONE

    # a sessionmaker(), also in the same scope as the engine
    Session = sessionmaker(engine)

    # we can now construct a Session() without needing to pass the
    # engine each time
    with Session() as session:
        Session.configure(bind=engine)
        print(session.get_bind().table_names())

        res = session.query(Purchase).all()
        print("Purchase query results:")
        print(res)


    # session = Session()
    # print(session.get_bind().table_names())
    # print(session)
    return render_template('dummy.html')
