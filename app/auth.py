from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

from . import db
from .models import Settlement, User, UnconfirmedUser
from .mail import send_email_confirm_email, send_password_reset_email
from .forms import SignInForm, RegisterForm, ResetPasswordRequestForm, PasswordResetForm
from .functions import delete_unconfirmed_users

import datetime as dt


auth = Blueprint('auth', __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))
    error = None
    form = SignInForm()

    if form.validate_on_submit():
        email = form.email.data.lower()
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if not user:
            error = "Личного кабинета с такой электронной почтой не существует."
        elif check_password_hash(user.password, password):
            login_user(user)
            if current_user.id == 2:
                return redirect(url_for("views.security"))
            else:
                return redirect(url_for("views.transport_list"))
        else:
            error = "Неверный пароль, попробуйте еще раз."
    return render_template("login.html", form=form, error=error, logged_in=current_user.is_authenticated)


@auth.route("/register", methods=["GET", "POST"])
def register():
    delete_unconfirmed_users()
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))
    error = None
    register_form = RegisterForm()
    if register_form.validate_on_submit():

        hash_and_salted_password = generate_password_hash(register_form.password.data,
                                                          'pbkdf2:sha256',
                                                          8)
        email_in_use = User.query.filter_by(email=register_form.email.data).first()
        email_in_use2 = UnconfirmedUser.query.filter_by(email=register_form.email.data).first()
        if email_in_use:
            error = 'Данная почта уже используется, пожалуйста, нажмите кнопку "войти".'
        elif email_in_use2:
            error = 'Вам на почту уже отправлены инструкции для завершения регистрации.'
        elif register_form.password.data != register_form.repeat_password.data:
            error = 'Пароли не совпадают'
        else:
            new_user = UnconfirmedUser(first_name=register_form.first_name.data.title(),
                                       last_name=register_form.last_name.data.title(),
                                       settlement_id=int(register_form.settlement.data),
                                       plot_number=register_form.plot_number.data,
                                       email=register_form.email.data.lower(),
                                       password=hash_and_salted_password,
                                       time_msg_sent=dt.datetime.now())
            db.session.add(new_user)
            db.session.commit()
            send_email_confirm_email(new_user)
            flash('На почту выслано письмо с инструкциями для завершения регистрации. Оно активно в течение 5 минут. '
                  'Если не видите письма, проверьте папку "спам"')
            return redirect(url_for("auth.login"))
    return render_template("register.html", form=register_form,
                           error=error, logged_in=current_user.is_authenticated)


@auth.route("/confirm-register/<token>", methods=["GET", "POST"])
def confirm_email(token):
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))
    unconfirmed_user = UnconfirmedUser.verify_confirm_email_token(token)
    if not unconfirmed_user:
        flash('Высланный токен больше не активен, пожалуйста, попробуйте зарегистрироваться снова')
        return redirect(url_for('views.home'))
    else:
        confirmed_user = User(first_name=unconfirmed_user.first_name,
                              last_name=unconfirmed_user.last_name,
                              settlement_id=unconfirmed_user.settlement_id,
                              plot_number=unconfirmed_user.plot_number,
                              email=unconfirmed_user.email,
                              password=unconfirmed_user.password)
        db.session.add(confirmed_user)
        db.session.delete(unconfirmed_user)
        db.session.commit()
        flash('Вы успешно зарегистрировались')
    return redirect(url_for('auth.login'))


@auth.route('/reset-password-request', methods=["GET", "POST"])
def reset_password_request():
    error = None
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            send_password_reset_email(user)
            flash('На почту высланы инструкции для сброса пароля. Если не видите письма, проверьте папку "спам"')
            return redirect(url_for('auth.login'))
        else:
            error = 'Данная электронная почта не зарегистрирована'
    return render_template('reset-password-request.html', form=form,
                           logged_in=current_user.is_authenticated, error=error)


@auth.route('/reset-password/<token>', methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('views.home'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        hash_and_salted_password = generate_password_hash(form.password.data,
                                                          'pbkdf2:sha256',
                                                          8)
        user.password = hash_and_salted_password
        db.session.commit()
        flash("Пароль успешно обновлен")
        return redirect(url_for('auth.login'))
    return render_template('reset-password.html', token=token, form=form)


@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('views.home'))
