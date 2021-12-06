from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_babel import _, lazy_gettext as _l

from app.models.user import User
from app.models.game import Game


from flask import Blueprint
bp = Blueprint('users', __name__)


class LoginForm(FlaskForm):
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    remember_me = BooleanField(_l('Remember Me'))
    submit = SubmitField(_l('Sign In'))


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_auth(form.email.data, form.password.data)
        if user is None:
            flash('Invalid email or password')
            return redirect(url_for('users.login'))
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index.index')

        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


class RegistrationForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired(), Length(max=20, message="Maximum length of 20 characters")])
    email = StringField(_l('Email'), validators=[DataRequired(), Email(), Length(max=50, message="Maximum length of 50 characters")])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    password2 = PasswordField(
        _l('Repeat Password'), validators=[DataRequired(),
                                           EqualTo('password')])
    game = SelectField(_l('Game'), validate_choice=True, coerce=int)
    submit = SubmitField(_l('Register'))

    def validate_email(self, email):
        if User.email_exists(email.data):
            raise ValidationError(_('Already a user with this email.'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
    form = RegistrationForm()

    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, echo=True)
    Session = sessionmaker(engine, expire_on_commit=True)
    session = Session()
    games = session.query(Game).all()
    form.game.choices = [(g.game_id, g.game_name.title()) for g in games]

    if form.validate_on_submit():
        print('validated1')
        if User.register(form.email.data,
                         form.password.data,
                         form.username.data,
                         form.game.data):
            flash('Congratulations, you are now a registered user!')
            print("registered!")
            return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index.index'))
