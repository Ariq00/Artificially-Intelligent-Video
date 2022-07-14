from flask import flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, \
    EmailField
from wtforms.validators import DataRequired, EqualTo, ValidationError, Email
from models import User
from werkzeug.security import check_password_hash
from password_strength import PasswordPolicy

password_policy = PasswordPolicy.from_names(
    length=8,  # min length: 8
    uppercase=1,  # need min. 1 uppercase letters
    numbers=1,  # need min. 1 digits
)


class RegistrationForm(FlaskForm):
    first_name = StringField(label='First Name',
                             validators=[DataRequired()])
    last_name = StringField(label='Last Name',
                            validators=[DataRequired()])
    email = EmailField(label='Email Address',
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
        users = User.objects(email=email.data.lower())
        if users:
            raise ValidationError(
                'Email address already in use')

    def validate_password(self, password):
        if len(password_policy.test(password.data)) > 0:
            flash(
                "Password must be at least 8 characters and contain at least 1 uppercase character and 1 number",
                "danger")
            raise ValidationError(
                'Password must be at least 8 characters and contain at least 1 uppercase character and 1 number')


class LoginForm(FlaskForm):
    email = EmailField(label='Email address', validators=[DataRequired()])
    password = PasswordField(label='Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Log in')

    def validate_email(self, email):
        users = User.objects(email=email.data.lower())
        if not users:
            flash(f"Please check the email entered and try again.", 'danger')
            raise ValidationError(
                'No account associated with that email!')

    def validate_password(self, password):
        user = User.objects(email=self.email.data.lower()).first()
        if user:
            if not check_password_hash(user.password, password.data):
                flash(f"Please double check your password and try again",
                      'danger')
                raise ValidationError(
                    'Incorrect password. Please double-check and try again.')


class RequestPasswordResetForm(FlaskForm):
    email = EmailField(label='Email Address',
                       validators=[DataRequired(),
                                   Email(message="Invalid Email")])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        users = User.objects(email=email.data.lower())
        if not users:
            flash(f"Please check the email entered and try again.", 'danger')
            raise ValidationError(
                'No account associated with that email!')


class ResetPasswordForm(FlaskForm):
    password = PasswordField(label='Password', validators=[DataRequired()])
    password_repeat = PasswordField(
        label='Confirm Password',
        validators=[DataRequired(),
                    EqualTo('password',
                            message='Passwords must match')])
    submit = SubmitField('Reset Password')

    def validate_password(self, password):
        if len(password_policy.test(password.data)) > 0:
            flash(
                "Password must be at least 8 characters and contain at least 1 uppercase character and 1 number",
                "danger")
            raise ValidationError(
                'Password must be at least 8 characters and contain at least 1 uppercase character and 1 number')


class UpdateAccountForm(FlaskForm):
    email = EmailField(label='New email address', validators=[])
    password = PasswordField(label='New password', validators=[])
    password_repeat = PasswordField(
        label='Confirm new password',
        validators=[EqualTo('password',
                            message='Passwords must match')])
    submit = SubmitField('Update Account Details')

    def validate_email(self, email):
        users = User.objects(email=email.data.lower())
        if users:
            raise ValidationError(
                'Email address already in use')

    def validate_password(self, password):
        if password.data:
            if len(password_policy.test(password.data)) > 0:
                flash(
                    "Password must be at least 8 characters and contain at least 1 uppercase character and 1 number",
                    "danger")
                raise ValidationError(
                    'Password must be at least 8 characters and contain at least 1 uppercase character and 1 number')
