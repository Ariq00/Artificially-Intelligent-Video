from flask import flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, \
    EmailField
from wtforms.validators import DataRequired, EqualTo, ValidationError, Email
from models import User
from werkzeug.security import check_password_hash


class RegistrationForm(FlaskForm):
    first_name = StringField(label='First name',
                             validators=[DataRequired()])
    last_name = StringField(label='Last name',
                            validators=[DataRequired()])
    email = EmailField(label='Email address',
                       validators=[DataRequired(),
                                   Email(message="Invalid Email")])
    password = PasswordField(label='Password', validators=[DataRequired()])
    password_repeat = PasswordField(
        label='Confirm Password',
        validators=[DataRequired(),
                    EqualTo('password',
                            message='Passwords must match')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        users = User.objects(email=email.data)
        if users:
            raise ValidationError(
                'Email address already in use')


class LoginForm(FlaskForm):
    email = EmailField(label='Email address', validators=[DataRequired()])
    password = PasswordField(label='Password', validators=[DataRequired()])
    remember = BooleanField('Keep me signed in')
    submit = SubmitField('Log in')

    def validate_email(self, email):
        users = User.objects(email=email.data)
        if not users:
            flash(f"Please chck the email entered and try again.", 'danger')
            raise ValidationError(
                'No email associated with that account!')

    def validate_password(self, password):
        user = User.objects(email=self.email.data).first()
        if not check_password_hash(user.password, password.data):
            flash(f"Please double check your password and try again", 'danger')
            raise ValidationError(
                'Incorrect password. Please double-check and try again.')
