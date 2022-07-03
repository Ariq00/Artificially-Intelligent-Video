from flask import Blueprint, render_template, flash, redirect, url_for
from werkzeug.security import generate_password_hash
from auth.forms import RegistrationForm, LoginForm
from models import User
from datetime import timedelta
from flask_login import login_user, logout_user, login_required, current_user

auth_bp = Blueprint('auth_bp', __name__)


@auth_bp.route("/register", methods=["POST", "GET"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(
            password=hashed_password,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
        )
        user.save()
        flash(f"Thank you for signing up {form.first_name.data}!", 'success')
        login_user(user)
        return redirect(url_for('home'))

    return render_template('register.html', title='Register', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.objects(email=form.email.data).first()
        login_user(user, remember=form.remember.data,
                   duration=timedelta(minutes=60))
        flash(f"Welcome {current_user.first_name}. You are now logged in!",
              'success')
        return redirect(url_for('home'))
    return render_template('login.html', title='Login', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash(f"You have been logged out", 'info')
    return redirect(url_for('home'))


@auth_bp.route('/my_account')
@login_required
def my_account():
    return render_template("my_account.html")
