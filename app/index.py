from flask import render_template, redirect
from flask_login import current_user
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.product import Product
from app.models.purchase import Purchase
from app.models.trainer import Trainer
from app.models.trainer_pokemon import TrainerPokemon
from app.models.user import User

from app.scoring_algo import score_teams
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
            trainer1 = session.query(Trainer).filter(Trainer.trainer_id==2).one_or_none()
            trainer2 = session.query(Trainer).filter(Trainer.trainer_id==4).one_or_none()
            trainer1_pkmn = trainer1.trainer_pokemon
            trainer2_pkmn = trainer2.trainer_pokemon
            print(score_teams(trainer2_pkmn, trainer1_pkmn))

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


@bp.route('/fight/', defaults={'trainer': 'dummy'})
@bp.route('/fight/<trainer>')
def fight(trainer):
    if not current_user.is_authenticated:
        return redirect("/login", code=302)
    print("THIS IS MY TRAINER", trainer)
    if trainer == 'dummy':
        return redirect("/leaders", code=302)
    
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, echo=True) #TODO: GET FROM OTHER ONE
    Session = sessionmaker(engine, expire_on_commit=False)
    session = Session()
    trainer_name = trainer.replace("%20", " ")
    user = session.query(User).filter(User.uid == current_user.uid).one_or_none()
    trainer = session.query(Trainer).filter(Trainer.name == trainer_name, Trainer.game_id==user.trainers[0].game_id).one_or_none()
    # user_trainer = user.trainers[0] // TODO: ONCE USER CAN ADD POKEMON, INPUT HERE
    dummy_trainer = session.query(Trainer).filter(Trainer.trainer_id == 2).one_or_none()


    return render_template('fight.html', trainer=trainer, user_trainer=dummy_trainer)

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
    if not current_user.is_authenticated:
        return redirect("/login", code=302)
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, echo=True) #TODO: GET FROM OTHER ONE
    Session = sessionmaker(engine, expire_on_commit=False)
    session = Session()
    trainers = session.query(Trainer).filter(Trainer.game_id == current_user.trainers[0].game_id, Trainer.is_user == False).all() # TODO: VERIFY DOESN'T INCLUDE USERS
    trainer_types = []
    for t in trainers:
        pokemon = [p.pokemon for p in t.trainer_pokemon]
        all_types = [p.type1.type_name for p in pokemon] + [p.type2.type_name for p in pokemon if p.type2 is not None]
        all_type_counts = [(t, all_types.count(t)) for t in set(all_types)]
        all_types_sorted = sorted(all_type_counts, key=lambda x: -1*x[1])
        trainer_types.append([k[0] for k in all_types_sorted[:2]])

    return render_template('leaders.html', trainers=trainers, trainer_types=trainer_types)

@bp.route('/pokemon/<int:id>')
def pokemon(id):
    if not current_user.is_authenticated: #TODO: verify that current user owns the pokemon
        return redirect("/login", code=302)
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, echo=True) #TODO: GET FROM OTHER ONE
    Session = sessionmaker(engine, expire_on_commit=False)
    session = Session()
    pokemon = session.query(TrainerPokemon).filter(TrainerPokemon.tp_id == id).one_or_none()
    return render_template('pokemon.html', pokemon = pokemon)
