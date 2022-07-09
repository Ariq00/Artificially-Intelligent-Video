from flask import Blueprint, render_template, flash, redirect, url_for
from werkzeug.security import generate_password_hash
from auth.forms import (RegistrationForm, LoginForm,
                        RequestPasswordResetForm, ResetPasswordForm,
                        UpdateAccountForm)
from models import User
from datetime import timedelta
from flask_login import login_user, logout_user, login_required, current_user
from setup_app import login_manager
from main.utilities import send_email

auth_bp = Blueprint('auth', __name__)


@auth_bp.route("/register", methods=["POST", "GET"])
def register():
    if current_user.is_authenticated:
        flash(f"You are already logged in!",
              'info')
        return redirect(url_for('main.home'))

    else:
        form = RegistrationForm()
        if form.validate_on_submit():
            hashed_password = generate_password_hash(form.password.data)
            user = User(
                password=hashed_password,
                email=form.email.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                email_verified=False
            )
            user.save()
            token = user.get_token(expires_sec=3600 * 24)
            subject = "Confirm your Email Address"
            msg_body = f"Hi {user.first_name},\n\n" \
                       f"Confirm your email using the following link:\n\n" \
                       f"{url_for('auth.verify_email', token=token, _external=True)}"
            send_email(subject, msg_body, user.email)

            flash(
                f"Thank you for signing up {form.first_name.data}! Please verify your email to complete registration.",
                'info')
            return redirect(url_for('auth.login'))

        return render_template('register.html', title='Register', form=form)


@auth_bp.route('/verify_email/<token>', methods=['GET', 'POST'])
def verify_email(token):
    user = User.verify_token(token)

    if not user:
        flash("Token is invalid. It may have expired.", "danger")
        return redirect(url_for('auth.login'))

    # Update the email address for user
    if user.new_email != "":
        user.email = user.new_email
        user.new_email = ""

    user.email_verified = True
    user.save()

    login_user(user)

    flash("Your email has been successfully verified!", "success")
    return redirect(url_for('main.home'))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.objects(email=form.email.data).first()
        if not user.email_verified:
            token = user.get_token(expires_sec=3600 * 24)
            subject = "Confirm your Email Address"
            msg_body = f"Hi {user.first_name},\n\nYou requested another email confirmation link. Confirm your email using the following link:\n\n{url_for('auth.verify_email', token=token, _external=True)}"
            send_email(subject, msg_body, user.email)

            flash(
                "Please verify your email first! Another verification email has been sent",
                "warning")
            return redirect(url_for('auth.login'))

        login_user(user, remember=form.remember.data,
                   duration=timedelta(minutes=60))
        flash(f"Welcome {current_user.first_name}. You are now logged in!",
              'success')
        return redirect(url_for('main.home'))

    return render_template('login.html', title='Login', form=form)


@auth_bp.route('/my_account', methods=['GET', 'POST'])
@login_required
def my_account():
    form = UpdateAccountForm()

    if form.validate_on_submit():

        if form.password.data:
            current_user.password = generate_password_hash(form.password.data)
            flash("Password updated successfully.", "success")

        if form.email.data:
            current_user.new_email = form.email.data

            token = current_user.get_token(expires_sec=3600 * 24)
            subject = "Confirm Your New Email Address"
            msg_body = f"Hi {current_user.first_name},\n\n" \
                       f"Confirm your email using the following link:\n\n" \
                       f"{url_for('auth.verify_email', token=token, _external=True)}"
            send_email(subject, msg_body, current_user.new_email)
            flash(
                "Verification email has been sent to new email address."
                " Until this is verified, your email address will stay the same ",
                "info")

    current_user.save()
    return render_template("my_account.html", title='My Account', form=form)


@auth_bp.route('/request_password_reset', methods=['GET', 'POST'])
def request_password_reset():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestPasswordResetForm()

    if form.validate_on_submit():
        user = User.objects(email=form.email.data).first()
        reset_token = user.get_token()
        subject = "Your Password Reset Request"
        recipient_email = user.email

        msg_body = f"Hi {user.first_name},\n\n" \
                   f"Reset your password through the following link:" \
                   f"\n\n{url_for('auth.reset_password', reset_token=reset_token, _external=True)}" \
                   f"\n\nPlease ignore this email if you did not make this request."

        send_email(subject, msg_body, recipient_email)
        flash(
            "An email containing a link to reset your password has been sent!",
            "info")
        return redirect(url_for('auth.login'))

    return render_template('request_password_reset.html',
                           title="Forgot Password",
                           form=form)


@auth_bp.route('/reset_password/<reset_token>', methods=['GET', 'POST'])
def reset_password(reset_token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_token(reset_token)

    if not user:
        flash("Token is invalid. It may have expired.", "danger")
        return redirect(url_for('auth.request_password_reset'))

    form = ResetPasswordForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user.password = hashed_password
        user.save()
        flash(f"Your password has been successfully reset!",
              'success')
        login_user(user)
        return redirect(url_for('main.home'))

    return render_template('reset_token.html',
                           title="Forgot Password",
                           form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash(f"You have been logged out", 'info')
    return redirect(url_for('main.home'))


@login_manager.user_loader
def load_user(user_id):
    if user_id is not None:
        return User.objects(id=user_id).first()
    return None


@login_manager.unauthorized_handler
def unauthorised():
    flash('You must be logged in to view this page.', 'warning')
    return redirect(url_for('auth.login'))
