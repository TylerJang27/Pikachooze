from flask import render_template, redirect, flash, url_for
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.fields.core import IntegerField
from wtforms.validators import Optional, ValidationError, DataRequired, NumberRange, Length
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_babel import _, lazy_gettext as _l

from app.models.trainer import Trainer
from app.models.trainer_pokemon import TrainerPokemon, GenderClass
from app.models.can_learn import CanLearn
from app.models.user import User
from app.models.pokemon import Pokemon

from app.scoring_algo import score_teams, score_team_6
from app.config import Config
import uuid
import math

from flask import Blueprint

def hp_calc(base_stat, level):
    hp_IV = 0
    hp_EV = 0
    return math.floor(0.01 * (2 * base_stat + hp_IV + math.floor(0.25 * hp_EV)) * level) + level + 10

def stat_calc(base_stat, level):
    nature = 1
    IV = 0
    EV = 0
    return math.floor(((0.01 * (2 * base_stat + IV + math.floor(0.25 * EV)) * level) + 5) * nature)

def make_session():
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, echo=True)
    Session = sessionmaker(engine, expire_on_commit=False)
    return Session()

bp = Blueprint('index', __name__)
@bp.route('/')
def index():
    return render_template('index.html')
    
@bp.route('/faq')
def faq():
    return render_template('faq.html')

@bp.route('/fight/', defaults={'trainer': 'dummy'})
@bp.route('/fight/<trainer>')
def fight(trainer):
    if not current_user.is_authenticated:
        return redirect("/login", code=302)
    session = make_session()
    trainer_name = trainer.replace("%20", " ")
    user = session.query(User).filter(User.uid == current_user.uid).one_or_none()
    
    if trainer == 'dummy':
        if user.last_trainer is not None:
            return redirect("/fight/" + user.last_trainer, code=302)
        return redirect("/leaders", code=302)
    else:
        user.last_trainer = trainer
        session.add(user)
        session.commit()
    
    trainer = session.query(Trainer).filter(Trainer.name == trainer_name, Trainer.game_id==user.trainers[0].game_id, Trainer.is_user == False).one_or_none()
    if trainer is None:
        return redirect("/404"), 404, {"Refresh": "1; url=/404"}
    user_trainer = user.trainers[0]

    # score_results = [(k[0], k[1][0], k[1][1]) for k in score_teams(user_trainer.trainer_pokemon, trainer.trainer_pokemon)[::-1]]
    score_results, top_team, matchups = score_team_6(user_trainer.trainer_pokemon, trainer.trainer_pokemon)
    
    return render_template('fight.html', trainer=trainer, scores=score_results, top_team=top_team, matchups=matchups)

@bp.route('/inventory')
def inventory():
    if not current_user.is_authenticated:
        return redirect("/login", code=302)
    session = make_session()
    user = session.query(User).filter(User.uid == current_user.uid).one_or_none()
    trainer = session.query(Trainer).filter(Trainer.trainer_id == user.trainers[0].trainer_id).one_or_none()
    trainer.trainer_pokemon = sorted(trainer.trainer_pokemon, key=lambda p: -1 * p.level)
    pokemon = session.query(Pokemon).filter(Pokemon.generation_id == user.trainers[0].game.generation_id).all()
    pokemon_choices = [(p.poke_id, p.name) for p in pokemon]
    return render_template('inventory.html', trainer=trainer, pokemon_choices=pokemon_choices)

@bp.route('/leaders')
def leaders():
    if not current_user.is_authenticated:
        return redirect("/login", code=302)
    session = make_session()
    user = session.query(User).filter(User.uid == current_user.uid).one_or_none()
    trainers = session.query(Trainer).filter(Trainer.game_id == user.trainers[0].game_id, Trainer.is_user == False).all()
    trainer_types = []
    for t in trainers:
        pokemon = [p.pokemon for p in t.trainer_pokemon]
        all_types = [p.type1.type_name for p in pokemon] + [p.type2.type_name for p in pokemon if p.type2 is not None]
        all_type_counts = [(t, all_types.count(t)) for t in set(all_types)]
        all_types_sorted = sorted(all_type_counts, key=lambda x: -1*x[1])
        trainer_types.append([k[0] for k in all_types_sorted[:2]])

    return render_template('leaders.html', trainers=trainers, trainer_types=trainer_types)

@bp.route('/leader_inventory/<trainer>')
def leader_inventory(trainer):
    if not current_user.is_authenticated:
        return redirect("/login", code=302)
    session = make_session()
    trainer_name = trainer.replace("%20", " ")
    user = session.query(User).filter(User.uid == current_user.uid).one_or_none()
    trainer = session.query(Trainer).filter(Trainer.name == trainer_name, Trainer.game_id==user.trainers[0].game_id, Trainer.is_user == False).one_or_none()
    if trainer is None:
        return redirect("/404"), 404, {"Refresh": "1; url=/404"}
    return render_template('inventory.html', trainer=trainer, pokemon_choices = [])

@bp.route('/add/<int:id>')
def add(id):
    if not current_user.is_authenticated:
        return redirect("/login", code=302)
    session = make_session()
    user = session.query(User).filter(User.uid == current_user.uid).one_or_none()
    if len(user.trainers[0].trainer_pokemon) >= 20:
        return redirect("/inventory", code=302)
    added = TrainerPokemon()
    added.trainer_id = user.trainers[0].trainer_id
    added.poke_id = id
    pokemon = session.query(Pokemon).filter(Pokemon.poke_id == id).one_or_none()
    if pokemon is None:
        return redirect("/404"), 404, {"Refresh": "1; url=/404"}
    added.nickname = pokemon.name
    session.add(added)
    try:
        session.commit()
    except:
        return redirect("/404"), 404, {"Refresh": "1; url=/404"}
    print("THE NEW ID IS ", added.tp_id)
    return redirect(url_for('index.pokemonedit', id=added.uuid))

@bp.route('/delete/<id>')
def delete(id):
    if not current_user.is_authenticated:
        return redirect("/login", code=302)
    session = make_session()
    try:
        pokemon = session.query(TrainerPokemon).filter(TrainerPokemon.uuid == id).one_or_none()
    except:
        return redirect("/404"), 404, {"Refresh": "1; url=/404"}
    if pokemon is None or pokemon.trainer.added_by_id != current_user.uid:
        return redirect("/404"), 404, {"Refresh": "1; url=/404"}
    session.delete(pokemon)
    session.commit()
    return redirect(url_for('index.inventory'))

@bp.route('/evolve/<id>/<int:to_id>')
def evolve(id, to_id):
    if not current_user.is_authenticated:
        return redirect("/login", code=302)
    session = make_session()
    try:
        u = uuid.UUID(id)
        pokemon = session.query(TrainerPokemon).filter(TrainerPokemon.uuid == u).one_or_none()
    except:
        return redirect("/404"), 404, {"Refresh": "1; url=/404"}
    if pokemon is None or pokemon.trainer.added_by_id != current_user.uid:
        return redirect("/404"), 404, {"Refresh": "1; url=/404"}
    evolution = [p.poke2.poke_id for p in pokemon.pokemon.evolutions]
    if to_id in evolution:
        old_name = pokemon.nickname
        evolution_index = evolution.index(to_id)
        new_name = pokemon.pokemon.evolutions[evolution_index].poke2.name
        if old_name == pokemon.pokemon.name:
            pokemon.nickname = new_name 
        pokemon.poke_id = to_id
        session.add(pokemon)
        session.commit()
        return redirect("/pokemon/"+ id, code=302)
    return redirect("/404"), 404, {"Refresh": "1; url=/404"}

@bp.route('/devolve/<id>/<int:to_id>')
def devolve(id, to_id):
    if not current_user.is_authenticated:
        return redirect("/login", code=302)
    session = make_session()
    try:
        u = uuid.UUID(id)
        pokemon = session.query(TrainerPokemon).filter(TrainerPokemon.uuid == u).one_or_none()
    except:
        return redirect("/404"), 404, {"Refresh": "1; url=/404"}
    if pokemon is None or pokemon.trainer.added_by_id != current_user.uid:
        return redirect("/404"), 404, {"Refresh": "1; url=/404"}
    devolution = [p.poke1.poke_id for p in pokemon.pokemon.devolutions]
    if to_id in devolution:
        old_name = pokemon.nickname
        devolution_index = devolution.index(to_id)
        new_name = pokemon.pokemon.devolutions[devolution_index].poke1.name
        if old_name == pokemon.pokemon.name:
            pokemon.nickname = new_name 
        pokemon.poke_id = to_id
        session.add(pokemon)
        session.commit()
        return redirect("/pokemon/"+ id, code=302)
    return redirect("/404"), 404, {"Refresh": "1; url=/404"}

@bp.route('/pokemon/<id>')
def pokemon(id):
    if not current_user.is_authenticated:
        return redirect("/login", code=302)
    session = make_session()
    try:
        u = uuid.UUID(id)
        pokemon = session.query(TrainerPokemon).filter(TrainerPokemon.uuid == u).one_or_none()
    except:
        return redirect("/404"), 404, {"Refresh": "1; url=/404"}
    if pokemon is None:
        return redirect("/404"), 404, {"Refresh": "1; url=/404"}
    evolution = [p.poke2 for p in pokemon.pokemon.evolutions]
    devolution = [p.poke1 for p in pokemon.pokemon.devolutions]
    stats = {"hp": pokemon.custom_hp, "attack": pokemon.custom_attack_stat, "defense": pokemon.custom_defense_stat, "sp_attack" : pokemon.custom_special_attack_stat,
    "sp_defense" : pokemon.custom_special_defense_stat, "speed": pokemon.custom_speed}
    if stats["hp"] is None:
        stats["hp"] = hp_calc(pokemon.pokemon.pokemon_base_stats[0].hp, pokemon.level)
    if stats["attack"] is None:
        stats["attack"] = stat_calc(pokemon.pokemon.pokemon_base_stats[0].attack_stat, pokemon.level)
    if stats["defense"] is None:
        stats["defense"] = stat_calc(pokemon.pokemon.pokemon_base_stats[0].defense_stat, pokemon.level)
    if stats["sp_attack"] is None:
        stats["sp_attack"] = stat_calc(pokemon.pokemon.pokemon_base_stats[0].special_attack_stat, pokemon.level)
    if stats["sp_defense"] is None:
        stats["sp_defense"] = stat_calc(pokemon.pokemon.pokemon_base_stats[0].special_defense_stat, pokemon.level)
    if stats["speed"] is None:
        stats["speed"] = stat_calc(pokemon.pokemon.pokemon_base_stats[0].speed, pokemon.level)
    moves = []
    for m in [pokemon.move1, pokemon.move2, pokemon.move3, pokemon.move4]:
        if m is not None:
            moves.append(m)
    read_only = pokemon.trainer.added_by is None or (pokemon.trainer.added_by.uid != current_user.uid)
    print(read_only)
    return render_template('pokemon.html', pokemon=pokemon, moves=moves, evolution=evolution, devolution=devolution, stats=stats, read_only=read_only)

class EditForm(FlaskForm):
    nickname = StringField(_l('Nickname:'), validators=[Length(max=25, message="Maximum length of 25 characters")])
    gender = SelectField(_l('Gender:'), validate_choice=True, coerce=int)
    level = IntegerField(_l('Level:'), validators=[DataRequired(), NumberRange(min=1, max=100, message='Must enter a number between 1 and 100')])
    hp = IntegerField(_l('HP:'), validators=[Optional(), NumberRange(min=1, max=4000, message='Must enter a number greater than 0')], render_kw={"placeholder": "Optional"})
    attack = IntegerField(_l('Attack:'), validators=[Optional(), NumberRange(min=1, max=4000, message='Must enter a number greater than 0')], render_kw={"placeholder": "Optional"})
    defense = IntegerField(_l('Defense:'), validators=[Optional(), NumberRange(min=1, max=4000, message='Must enter a number greater than 0')], render_kw={"placeholder": "Optional"})
    special_attack = IntegerField(_l('Special Attack:'), validators=[Optional(), NumberRange(min=1, max=4000, message='Must enter a number greater than 0')], render_kw={"placeholder": "Optional"})
    special_defense = IntegerField(_l('Special Defense:'), validators=[Optional(), NumberRange(min=1, max=4000, message='Must enter a number greater than 0')], render_kw={"placeholder": "Optional"})
    speed = IntegerField(_l('Speed:'), validators=[Optional(), NumberRange(min=1, max=4000, message='Must enter a number greater than 0')], render_kw={"placeholder": "Optional"})
    move1 = SelectField(_l('Move 1'), coerce=int)
    move2 = SelectField(_l('Move 2'), coerce=int)
    move3 = SelectField(_l('Move 3'), coerce=int)
    move4 = SelectField(_l('Move 4'), coerce=int)
    submit = SubmitField(_l('Save'))

    def validate_move1(self, move1):
        if move1.data == -1:
            raise ValidationError(_('Please select a move'))
        elif move1.data in [self.move2.data, self.move3.data, self.move4.data]:
            raise ValidationError(_('Please select unique moves'))
    def validate_move2(self, move2):
        if move2.data != -1 and move2.data in [self.move1.data, self.move3.data, self.move4.data]:
            raise ValidationError(_('Please select unique moves'))
    def validate_move3(self, move3):
        if move3.data != -1 and move3.data in [self.move1.data, self.move2.data, self.move4.data]:
            raise ValidationError(_('Please select unique moves'))
    def validate_move4(self, move4):
        if move4.data != -1 and move4.data in [self.move1.data, self.move2.data, self.move3.data]:
            raise ValidationError(_('Please select unique moves'))

@bp.route('/pokemonedit/<id>', methods=['GET', 'POST'])
def pokemonedit(id):
    if not current_user.is_authenticated:
        return redirect("/login", code=302)
    session = make_session()
    try:
        u = uuid.UUID(id)
        pokemon = session.query(TrainerPokemon).filter(TrainerPokemon.uuid == u).one_or_none()
    except:
        return redirect("/404"), 404, {"Refresh": "1; url=/404"}
    if pokemon is None or pokemon.trainer.added_by_id != current_user.uid:
        return redirect("/404"), 404, {"Refresh": "1; url=/404"}
    available_moves = session.query(CanLearn).filter(CanLearn.poke_id == pokemon.poke_id).all()
    move_choices = [(-1, "")] + [(move.move.move_id, move.move.move_name) for move in available_moves]
    moves = []


    for m in [pokemon.move1, pokemon.move2, pokemon.move3, pokemon.move4]:
        if m is not None:
            moves.append(m.move_name)
        else:
            moves.append("")
    form = EditForm()
    form.move1.choices = move_choices
    form.move2.choices = move_choices
    form.move3.choices = move_choices
    form.move4.choices = move_choices
    form.gender.choices = [(GenderClass.male.value, "Male"), (GenderClass.female.value, "Female")]
    
    if form.validate_on_submit():
        curr_pokemon = session.query(TrainerPokemon).filter(TrainerPokemon.uuid == u).one_or_none()
        curr_pokemon.nickname = form.nickname.data if form.nickname.data != "" else curr_pokemon.pokemon.name
        curr_pokemon.gender = {1: "male", 2: "female"}[form.gender.data]
        curr_pokemon.level = form.level.data

        curr_pokemon.custom_hp = form.hp.data
        curr_pokemon.custom_attack_stat = form.attack.data
        curr_pokemon.custom_defense_stat = form.defense.data
        curr_pokemon.custom_special_attack_stat = form.special_attack.data
        curr_pokemon.custom_special_defense_stat = form.special_defense.data 
        curr_pokemon.custom_speed = form.speed.data

        curr_pokemon.move1_id = form.move1.data if form.move1.data != -1 else None
        curr_pokemon.move2_id = form.move2.data if form.move2.data != -1 else None
        curr_pokemon.move3_id = form.move3.data if form.move3.data != -1 else None
        curr_pokemon.move4_id = form.move4.data if form.move4.data != -1 else None

        session.add(curr_pokemon)
        session.commit()
        return redirect(url_for('index.pokemon', id=u))
    form.nickname.data = pokemon.nickname
    form.gender.data = pokemon.gender.value
    form.level.data = pokemon.level

    form.hp.data = pokemon.custom_hp 
    form.attack.data = pokemon.custom_attack_stat 
    form.defense.data = pokemon.custom_defense_stat 
    form.special_attack.data = pokemon.custom_special_attack_stat 
    form.special_defense.data = pokemon.custom_special_defense_stat 
    form.speed.data = pokemon.custom_speed 

    form.move1.data = pokemon.move1_id
    form.move2.data = pokemon.move2_id
    form.move3.data = pokemon.move3_id
    form.move4.data = pokemon.move4_id
    
    return render_template('pokemonedit.html', pokemon=pokemon, moves=moves, form=form, move_choices=move_choices)
