from flask import render_template
from flask_login import current_user
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.product import Product
from app.models.purchase import Purchase
from app.models.trainer import Trainer
from app.config import Config

from flask import Blueprint
bp = Blueprint('index', __name__)


@bp.route('/')
def index():

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

        # get all available products for sale:
        # products = Product.get_all(True)
        # products = session.query(Product).all()
        products = []

        # find the products current user has bought:
        if current_user.is_authenticated:
            # purchases = Purchase.get_all_by_uid_since(
                # current_user.id, datetime.datetime(1980, 9, 14, 0, 0, 0))
            # purchases = session.query(Purchase).all()
            print(current_user, current_user.trainers, current_user.trainers[0].trainer_pokemon if len(current_user.trainers) > 0 else "NO POKEMON")
            purchases = []
            print("There would have been purchases!")
        else:
            purchases = None
        # render the page by adding information to the index.html file
        return render_template('index.html',
                            avail_products=products,
                            purchase_history=purchases)
    # session = Session()
    # print(session.get_bind().table_names())
    # print(session)
    # return render_template('dummy.html')
    
@bp.route('/faq')
def faq():
    return render_template('faq.html')

@bp.route('/fight')
def fight():
    return render_template('fight.html')

@bp.route('/inventory')
def inventory():
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, echo=True) #TODO: GET FROM OTHER ONE
    Session = sessionmaker(engine, expire_on_commit=False)
    session = Session()
    trainer = session.query(Trainer).filter(Trainer.trainer_id == 2).one_or_none()
    print([p.pokemon.type1 for p in trainer.trainer_pokemon])
    return render_template('inventory.html', trainer=trainer)

@bp.route('/leaders')
def leaders():
    return render_template('leaders.html')
