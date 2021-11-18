from flask import render_template, redirect, flash, url_for
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.fields.core import IntegerField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_babel import _, lazy_gettext as _l

from app.models.purchase import Purchase
from app.models.trainer import Trainer
from app.models.trainer_pokemon import TrainerPokemon, GenderClass
from app.models.can_learn import CanLearn
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
    dummy_trainer = session.query(Trainer).filter(Trainer.trainer_id == 4).one_or_none()
    user_trainer = dummy_trainer

    score_results = score_teams(user_trainer.trainer_pokemon, trainer.trainer_pokemon)[::-1]
    # print(score_results)

    return render_template('fight.html', trainer=trainer, scores=score_results)

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
    if not current_user.is_authenticated: #TODO: verify that current user owns the pokemon or is trainer
        return redirect("/login", code=302)
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, echo=True) #TODO: GET FROM OTHER ONE
    Session = sessionmaker(engine, expire_on_commit=False)
    session = Session()
    pokemon = session.query(TrainerPokemon).filter(TrainerPokemon.tp_id == id).one_or_none()
    moves = []
    for m in [pokemon.move1, pokemon.move2, pokemon.move3, pokemon.move4]:
        if m is not None:
            moves.append(m)
    return render_template('pokemon.html', pokemon=pokemon, moves=moves)

class EditForm(FlaskForm):
    nickname = StringField(_l('Nickname:'))
    gender = SelectField(_l('Gender:'), validate_choice=True, coerce=int)
    level = IntegerField(_l('Level:'), validators=[DataRequired()])
    hp = IntegerField(_l('HP:'))
    attack = IntegerField(_l('Attack:'))
    defense = IntegerField(_l('Defense:'))
    special_attack = IntegerField(_l('Special Attack:'))
    special_defense = IntegerField(_l('Special Defense:'))
    speed = IntegerField(_l('Speed:'))
    # move1 = IntegerField(_l('Move 1'), validators=[DataRequired()])
    # move2 = IntegerField(_l('Move 2'))
    # move3 = IntegerField(_l('Move 3'))
    # move4 = IntegerField(_l('Move 4'))
    submit = SubmitField(_l('Save'))

@bp.route('/pokemonedit/<int:id>', methods=['GET', 'POST'])
def pokemonedit(id):
    if not current_user.is_authenticated: #TODO: verify that current user owns the pokemon
        return redirect("/login", code=302)
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, echo=False) #TODO: GET FROM OTHER ONE
    Session = sessionmaker(engine, expire_on_commit=False)
    session = Session()
    pokemon = session.query(TrainerPokemon).filter(TrainerPokemon.tp_id == id).one_or_none()
    available_moves = session.query(CanLearn).filter(CanLearn.poke_id == pokemon.poke_id).all()
    moves = []
    for m in [pokemon.move1, pokemon.move2, pokemon.move3, pokemon.move4]:
        if m is not None:
            moves.append(m)
    form = EditForm()
    form.nickname.data = pokemon.nickname
    form.gender.choices = [(GenderClass.male.value, "Male"), (GenderClass.female.value, "Female")]
    form.gender.data = 2
    form.level.data = pokemon.level
    
    print("about to validate")
    if form.validate_on_submit():
        # TODO: DO WE NEED AN ELSE
        print("form has been submitted", form.nickname.data, form.level.data)
        # flash("Test")
        return redirect(url_for('index.pokemonedit', id=id))
    
    return render_template('pokemonedit.html', pokemon=pokemon, moves=moves, available_moves=available_moves, form=form)
