from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FileField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User

class LoginForm(FlaskForm):
    email = StringField('Sähköposti', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    password = PasswordField('Salasana', validators=[DataRequired()])
    remember_me = BooleanField('Pidä minut kirjautuneena sisään')
    submit = SubmitField('Lähetä')


class RegistrationForm(FlaskForm):
    email = StringField('Sähköposti', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    username = StringField('Käyttäjätunnus', validators=[
        DataRequired(), Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
               'Usernames must have only letters, numbers, dots or '
               'underscores')])
    password = PasswordField('Salasana', validators=[
        DataRequired(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Vahvista salasana', validators=[DataRequired()])
    submit = SubmitField('Lähetä')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('Sähköposti jo rekisteröitynyt.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Käyttäjänimi on jo käytössä.')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Vanha salasana', validators=[DataRequired()])
    password = PasswordField('Uusi salasana', validators=[
        DataRequired(), EqualTo('password2', message='Salasanojen täytyy täsmätä.')])
    password2 = PasswordField('Vahvista uusi salasana',
                              validators=[DataRequired()])
    submit = SubmitField('Päivitä salasana')


class PasswordResetRequestForm(FlaskForm):
    email = StringField('Sähköposti', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    submit = SubmitField('Päivitä salasana')


class PasswordResetForm(FlaskForm):
    password = PasswordField('Uusi salasana', validators=[
        DataRequired(), EqualTo('password2', message='Salasanojen täytyy täsmätä.')])
    password2 = PasswordField('Vahvista salasana', validators=[DataRequired()])
    submit = SubmitField('Päivitä salasana')


class ChangeEmailForm(FlaskForm):
    email = StringField('Uusi sähköposti', validators=[DataRequired(), Length(1, 64),
                                                 Email()])
    password = PasswordField('Salasana', validators=[DataRequired()])
    submit = SubmitField('Päivitä sähköposti')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('Sähköposti on jo rekisteröity.')

class ProfileForm(FlaskForm):
    file = FileField('Kuva')

    username = StringField('Käyttäjätunnus', validators=[
            DataRequired(), Length(1, 64),
            Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                'Usernames must have only letters, numbers, dots or '
                'underscores')])

    email = StringField('Sähköposti', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    
    password = PasswordField('Salasana', validators=[
        DataRequired(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Vahvista salasana', validators=[DataRequired()])

    submit = SubmitField('Lähetä')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('Sähköposti on jo rekisteröity.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Käyttäjänimi on jo käytössä.')


class UusiKayttaja(FlaskForm):
    file = FileField('Kuva')

    username = StringField('Käyttäjätunnus', validators=[
        DataRequired(), Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
               'Usernames must have only letters, numbers, dots or '
               'underscores')])

    email = StringField('Sähköposti', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    
    password = PasswordField('Salasana', validators=[
        DataRequired(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Vahvista salasana', validators=[DataRequired()])
    

    submit = SubmitField('Lähetä')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('Sähköposti on jo rekisteröity.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Käyttäjänimi on jo käytössä.')

class PaivitaKayttaja(FlaskForm):
    file = FileField('Kuva')

    username = StringField('Käyttäjätunnus', validators=[
        DataRequired(), Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
               'Usernames must have only letters, numbers, dots or '
               'underscores')])

    email = StringField('Sähköposti', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    
    password = PasswordField('Uusi salasana', validators=[
        DataRequired(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Vahvista salasana', validators=[DataRequired()])
    
    submit = SubmitField('Lähetä')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')

class UusiTehtava(FlaskForm):
    nimi = StringField('Username', validators=[
            DataRequired(), Length(1, 64),
            Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                'Usernames must have only letters, numbers, dots or '
                'underscores')])
    
    submit = SubmitField('Lähetä')

class PaivitaTehtava(FlaskForm):
    nimi = StringField('Username', validators=[
                DataRequired(), Length(1, 64),
                Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                    'Usernames must have only letters, numbers, dots or '
                    'underscores')])
        
    submit = SubmitField('Lähetä')

