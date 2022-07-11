from flask import Flask, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey, Date, DateTime
from flask_bootstrap import Bootstrap
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_migrate import Migrate
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from forms import NewPassForm, SignInForm, NewTransportForm, UpdatePassForm, \
    RegisterForm, ResetPasswordRequestForm, PasswordResetForm, AddTaxiForm
from datetime import date
import datetime as dt
from time import time
import jwt
from flask_mail import Message, Mail
import os
from functools import wraps

# for adding environment variables with file .env
# from dotenv import load_dotenv
# load_dotenv('.env')


app = Flask(__name__)

# TODO: Try to create ConfigClass(object) (https://flask-user.readthedocs.io/en/latest/basic_app.html)


app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///car-pass.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
Bootstrap(app)

# TODO: Connect PostgreSQL


login_manager = LoginManager()
login_manager.init_app(app)
mail = Mail(app)


# -----------------CONFIGURE DB TABLES----------------------
class Settlement(db.Model):
    __tablename__ = "settlements"
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False, unique=True)
    residents = relationship("User", back_populates="settlement")


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    plot_number = Column(String(100), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)

    permanent_passes = relationship("PermanentPass", back_populates="owner")
    temporary_passes = relationship("TemporaryPass", back_populates="plot_owner")
    taxi_passes = relationship("TaxiPass", back_populates="plot_owner")
    settlement = relationship("Settlement", back_populates="residents")
    settlement_id = Column(Integer, ForeignKey("settlements.id"))

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            user_id = jwt.decode(token, app.config['SECRET_KEY'],
                                 algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(user_id)


class UnconfirmedUser(db.Model):
    __tablename__ = "unconfirmed_users"
    id = Column(Integer, primary_key=True)
    plot_number = Column(String(100), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    settlement_id = Column(Integer, nullable=False)
    time_msg_sent = Column(DateTime, nullable=False)

    def get_confirm_email_token(self, expires_in=600):
        return jwt.encode(
            {'confirm_email': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_confirm_email_token(token):
        try:
            unconfirmed_user_id = jwt.decode(token, app.config['SECRET_KEY'],
                                             algorithms=['HS256'])['confirm_email']
        except:
            return
        return UnconfirmedUser.query.get(unconfirmed_user_id)


class PermanentPass(db.Model):
    __tablename__ = "permanent_passes"
    id = Column(Integer, primary_key=True)
    # Vehicle Identification Number
    vin = Column(String(100), unique=True, nullable=False)
    car_model = Column(String(100), nullable=False)
    owner = relationship("User", back_populates="permanent_passes")
    owner_id = Column(Integer, ForeignKey("users.id"))


class TemporaryPass(db.Model):
    __tablename__ = "temporary_passes"
    id = Column(Integer, primary_key=True)
    # Vehicle Identification Number
    vin = Column(String(100), unique=True, nullable=False)
    car_model = Column(String(100), nullable=False)
    plot_owner = relationship("User", back_populates="temporary_passes")
    plot_owner_id = Column(Integer, ForeignKey("users.id"))
    expiry_date = Column(Date, nullable=False)


class TaxiPass(db.Model):
    __tablename__ = "taxi_passes"
    id = Column(Integer, primary_key=True)
    vin = Column(String(100))
    car_model = Column(String(100))
    color = Column(String(100))
    access_time = Column(Integer, nullable=False)
    plot_owner = relationship("User", back_populates="taxi_passes")
    plot_owner_id = Column(Integer, ForeignKey("users.id"))


db.create_all()


# -----------------CONFIGURE DB TABLES----------------------


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.get_id() == '1':
            return f(*args, **kwargs)
        else:
            return render_template('403.html')

    return decorated_function


def security_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.get_id() == '2':
            return f(*args, **kwargs)
        else:
            return render_template('403.html')

    return decorated_function


def delete_outdated_data(expire_time):
    """Deletes outdated transport passes in defined expire time (days)."""
    today = date.today()
    unconfirmed_users = UnconfirmedUser.query.all()
    taxi_list = TaxiPass.query.all()
    temporary_passes = TemporaryPass.query.all()
    for transport in temporary_passes:
        expiry_date = transport.expiry_date
        if (expiry_date - today).days > expire_time:
            db.session.delete(transport)
            db.session.commit()
    for taxi in taxi_list:
        expiration_time = dt.time(hour=taxi.access_time)
        if expiration_time < dt.datetime.today().time():
            db.session.delete(taxi)
            db.session.commit()
    for user in unconfirmed_users:
        if dt.datetime.now().minute - user.time_msg_sent.minute > 15:
            db.session.delete(user)
            db.session.commit()


def send_email(subject, sender, recipients, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.html = html_body
    mail.send(msg)


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('Сброс пароля',
               sender=app.config['MAIL_DEFAULT_SENDER'],
               recipients=[user.email],
               html_body=render_template('email/reset_password_text.html',
                                         user=user, token=token))


def send_email_confirm_email(user):
    token = user.get_confirm_email_token()
    send_email('Подтвердите адрес электронной почты',
               sender=app.config['MAIL_DEFAULT_SENDER'],
               recipients=[user.email],
               html_body=render_template('email/confirm_email_text.html',
                                         user=user, token=token))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


# ---------------------Web routes-----------------------
@app.route("/")
def home():
    delete_outdated_data(expire_time=7)
    if current_user.is_authenticated:
        return redirect(url_for('transport_list'))
    else:
        return redirect(url_for('login'))


@app.route("/transport-list", methods=["GET", "POST"])
def transport_list():
    delete_outdated_data(expire_time=7)
    temporary_passes = TemporaryPass.query.all()
    permanent_passes = PermanentPass.query.all()
    taxi_passes = TaxiPass.query.all()
    if current_user.is_authenticated:
        user_id = int(current_user.get_id())
    else:
        user_id = None
    return render_template("transport-list.html",
                           current_user=current_user,
                           temporary_passes=temporary_passes,
                           permanent_passes=permanent_passes,
                           taxi_passes=taxi_passes,
                           logged_in=current_user.is_authenticated,
                           id=user_id,
                           today=date.today())


@app.route("/new-pass", methods=["GET", "POST"])
def new_pass():
    error = None
    form = NewPassForm()
    if form.validate_on_submit():
        vin = form.vin.data.upper()
        car_model = form.car_model.data.upper()
        # form.validation_period.data returns amount of days as str
        expiry_date = dt.date.today() + dt.timedelta(int(form.validation_period.data))
        temporary_pass = TemporaryPass.query.filter_by(vin=vin).first()
        permanent_pass = PermanentPass.query.filter_by(vin=vin).first()
        if temporary_pass:
            error = f"У данного автомобиля уже есть пропуск до {temporary_pass.expiry_date.strftime('%d-%m-%Y')}"
        elif permanent_pass:
            error = f"Данный автомобиль уже добален в список личных транспортных средаств"
        else:
            new_temporary_pass = TemporaryPass(vin=vin,
                                               car_model=car_model,
                                               plot_owner_id=current_user.get_id(),
                                               expiry_date=expiry_date)
            db.session.add(new_temporary_pass)
            db.session.commit()
            return redirect(url_for("transport_list"))
    return render_template("new-pass.html", form=form, logged_in=current_user.is_authenticated, error=error)


@app.route("/add-transport", methods=["GET", "POST"])
def add_transport():
    error = None
    form = NewTransportForm()
    if form.validate_on_submit():
        vin = form.vin.data.upper()
        car_model = form.car_model.data.upper()

        permanent_pass = PermanentPass.query.filter_by(vin=vin).first()
        if permanent_pass:
            error = f"Транспорт с таким номером уже добавлен"
        else:
            new_permanent_pass = PermanentPass(vin=vin, car_model=car_model, owner_id=current_user.get_id())
            db.session.add(new_permanent_pass)
            db.session.commit()
            return redirect(url_for("transport_list"))
    return render_template("add-transport.html", form=form, logged_in=current_user.is_authenticated, error=error)


@app.route("/add-taxi", methods=["GET", "POST"])
def add_taxi():
    form = AddTaxiForm()
    if form.validate_on_submit():
        vin = form.vin.data.upper()
        car_model = form.car_model.data.upper()
        access_time = form.access_time.data
        new_taxi_pass = TaxiPass(vin=vin,
                                 car_model=car_model,
                                 plot_owner_id=current_user.get_id(),
                                 access_time=int(access_time))
        db.session.add(new_taxi_pass)
        db.session.commit()
        return redirect(url_for('transport_list'))
    return render_template('add-taxi.html', form=form, logged_in=current_user.is_authenticated)


@app.route("/login", methods=["GET", "POST"])
def login():
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
                return redirect(url_for("security"))
            else:
                return redirect(url_for("transport_list"))
        else:
            error = "Неверный пароль, попробуйте еще раз."
    return render_template("login.html", form=form, error=error, logged_in=current_user.is_authenticated)


@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    register_form = RegisterForm()
    if register_form.validate_on_submit():

        hash_and_salted_password = generate_password_hash(register_form.password.data,
                                                          'pbkdf2:sha256',
                                                          8)
        user = User.query.filter_by(plot_number=register_form.plot_number.data).first()
        email_in_use = User.query.filter_by(email=register_form.email.data).first()
        email_in_use2 = UnconfirmedUser.query.filter_by(email=register_form.email.data).first()
        if user:
            error = 'Для данного участка уже имеется личный кабинет, пожалуйста, нажмите кнопку "войти".'
        elif email_in_use:
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
            flash('На почту выслано письмо для подтверждения электронной почты. Если не видите письма, проверьте '
                  'папку "спам"')
            return redirect(url_for("login"))
    return render_template("register.html", form=register_form,
                           error=error, logged_in=current_user.is_authenticated)


@app.route("/confirm-register/<token>", methods=["GET", "POST"])
def confirm_email(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    unconfirmed_user = UnconfirmedUser.verify_confirm_email_token(token)
    if not unconfirmed_user:
        print('No result')
        return redirect(url_for('home'))
    else:
        print('should work')
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
    return redirect(url_for('login'))


@app.route('/reset-password-request', methods=["GET", "POST"])
def reset_password_request():
    error = None
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            send_password_reset_email(user)
            flash('На почту высланы инструкции для сброса пароля. Если не видите письма, проверьте папку "спам"')
            return redirect(url_for('login'))
        else:
            error = 'Данная электронная почта не зарегистрирована'
    return render_template('reset-password-request.html', form=form,
                           logged_in=current_user.is_authenticated, error=error)


@app.route('/reset-password/<token>', methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('home'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        hash_and_salted_password = generate_password_hash(form.password.data,
                                                          'pbkdf2:sha256',
                                                          8)
        user.password = hash_and_salted_password
        db.session.commit()
        flash("Пароль успешно обновлен")
        return redirect(url_for('login'))
    return render_template('reset-password.html', token=token, form=form)


@app.route('/update/<int:pass_id>', methods=["GET", "POST"])
def update_pass(pass_id):
    pass_to_update = TemporaryPass.query.get(pass_id)
    update_form = UpdatePassForm()
    if update_form.validate_on_submit():
        pass_to_update.expiry_date = dt.date.today() + dt.timedelta(int(update_form.validation_period.data))
        db.session.commit()
        return redirect(url_for('transport_list'))
    return render_template('update-pass.html', pass_id=pass_id, form=update_form, pass_to_update=pass_to_update,
                           logged_in=current_user.is_authenticated)


@app.route('/delete-pass/<int:pass_id>')
def delete_pass(pass_id):
    pass_to_delete = TemporaryPass.query.get(pass_id)
    db.session.delete(pass_to_delete)
    db.session.commit()
    return redirect(url_for('transport_list'))


@app.route('/delete-transport/<int:transport_id>')
def delete_transport(transport_id):
    permanent_pass_to_delete = PermanentPass.query.get(transport_id)
    db.session.delete(permanent_pass_to_delete)
    db.session.commit()
    return redirect(url_for('transport_list'))


@app.route('/delete-taxi/<int:taxi_id>')
def delete_taxi(taxi_id):
    taxi_to_delete = TaxiPass.query.get(taxi_id)
    db.session.delete(taxi_to_delete)
    db.session.commit()
    return redirect(url_for('transport_list'))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/admin', methods=['GET', 'POST'])
@admin_only
def admin():
    users = User.query.all()
    temporary_passes = TemporaryPass.query.all()
    permanent_passes = PermanentPass.query.all()
    taxi_passes = TaxiPass.query.all()
    return render_template('admin.html', users=users,
                           temporary_passes=temporary_passes, permanent_passes=permanent_passes,
                           taxi_passes=taxi_passes, today=date.today(),
                           logged_in=current_user.is_authenticated)


@app.route('/admin/delete-user/<int:user_id>', methods=['GET', 'POST'])
@admin_only
def delete_user(user_id):
    user_to_delete = User.query.get(user_id)
    db.session.delete(user_to_delete)
    db.session.commit()
    return redirect(url_for('admin'))


@app.route('/security', methods=['GET'])
@security_only
def security():
    temporary_passes = TemporaryPass.query.all()
    permanent_passes = PermanentPass.query.all()
    taxi_passes = TaxiPass.query.all()
    return render_template('security.html', temporary_passes=temporary_passes, permanent_passes=permanent_passes,
                           taxi_passes=taxi_passes, today=date.today(), logged_in=current_user.is_authenticated)


if __name__ == "__main__":
    app.run(debug=True)
