from flask import Flask, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey, Date
from flask_bootstrap import Bootstrap
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from forms import NewPassForm, SignInForm, NewTransportForm, UpdatePassForm, \
    RegisterForm, ResetPasswordRequestForm, PasswordResetForm
from datetime import date, timedelta
from time import time
import jwt
from flask_mail import Message, Mail
import os

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
Bootstrap(app)


# TODO: Connect PostgreSQL


login_manager = LoginManager()
login_manager.init_app(app)
mail = Mail(app)


# -----------------CONFIGURE DB TABLES----------------------
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    plot_number = Column(Integer, unique=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)

    personal_transport = relationship("PersonalTransport", back_populates="owner")
    pass_transport = relationship("PassTransport", back_populates="plot_owner")

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


class PersonalTransport(db.Model):
    __tablename__ = "personal_transport"
    id = Column(Integer, primary_key=True)
    # Vehicle Identification Number
    vin = Column(String(100), unique=True)
    car_model = Column(String(100))
    owner = relationship("User", back_populates="personal_transport")
    plot_number = Column(Integer, ForeignKey("users.plot_number"))


class PassTransport(db.Model):
    __tablename__ = "pass_transport"
    id = Column(Integer, primary_key=True)
    # Vehicle Identification Number
    vin = Column(String(100), unique=True, nullable=False)
    car_model = Column(String(100))
    plot_owner = relationship("User", back_populates="pass_transport")
    plot_number = Column(Integer, ForeignKey("users.plot_number"))
    expiry_date = Column(Date, nullable=False)


db.create_all()


def delete_outdated_data(expire_time):
    """Deletes outdated transport passes in defined expire time (days)."""
    today = date.today()
    pass_transport = PassTransport.query.all()
    for transport in pass_transport:
        expiry_date = transport.expiry_date
        if (expiry_date - today).days > expire_time:
            db.session.delete(transport)
            db.session.commit()


def send_email(subject, sender, recipients, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.html = html_body
    mail.send(msg)


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('[НОВОВО 2] Сброс пароля',
               sender=app.config['MAIL_DEFAULT_SENDER'],
               recipients=[user.email],
               html_body=render_template('email/reset_password_text.html',
                                         user=user, token=token))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


# ---------------------Web routes-----------------------
@app.route("/")
def home():
    delete_outdated_data(expire_time=7)
    vehicles_pass_list = PassTransport.query.all()
    personal_transport_list = PersonalTransport.query.all()
    if current_user.is_authenticated:
        user_id = int(current_user.get_id())
    else:
        user_id = None
    return render_template('index.html',
                           pass_list=vehicles_pass_list,
                           transport_list=personal_transport_list,
                           logged_in=current_user.is_authenticated,
                           id=user_id,
                           today=date.today())


@app.route("/new-pass", methods=["GET", "POST"])
def new_pass():
    error = None
    form = NewPassForm()
    if form.validate_on_submit():
        new_vin = form.vin.data.upper()
        new_car_model = form.car_model.data.upper()
        # Variable expiry_date is datetime.date type
        new_expiry_date = form.validation_period.data
        pass_transport = PassTransport.query.filter_by(vin=new_vin).first()
        if pass_transport:
            error = f"У данного автомобиля уже есть пропуск до {pass_transport.expiry_date.strftime('%d-%m-%Y')}."
        else:
            plot_n = User.query.get(current_user.get_id()).plot_number
            new_pass_transport = PassTransport(vin=new_vin, car_model=new_car_model,
                                               plot_number=plot_n, expiry_date=new_expiry_date)
            db.session.add(new_pass_transport)
            db.session.commit()
            return redirect(url_for("home"))
    return render_template("new-pass.html", form=form, logged_in=current_user.is_authenticated, error=error)


@app.route("/add-transport", methods=["GET", "POST"])
def add_transport():
    form = NewTransportForm()
    if form.validate_on_submit():
        new_vin = form.vin.data.upper()
        new_car_model = form.car_model.data.upper()
        plot_n = User.query.get(current_user.get_id()).plot_number
        new_transport = PersonalTransport(vin=new_vin, car_model=new_car_model, plot_number=plot_n)
        db.session.add(new_transport)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("add-transport.html", form=form, logged_in=current_user.is_authenticated)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    form = SignInForm()
    if form.validate_on_submit():
        email = form.email.data.lower()
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        if not user:
            error = "Такого логина не существует, пожалуйста, попробуйте еще раз."
        elif check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("home"))
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
        if user:
            error = 'Для данного участка уже имеется личный кабинет, пожалуйста, нажмите кнопку "войти".'
        elif email_in_use:
            error = "Данный логин уже используется, пожалуйста, придумайте новый."
        else:
            new_user = User(first_name=register_form.first_name.data.title(),
                            last_name=register_form.last_name.data.title(),
                            plot_number=register_form.plot_number.data,
                            email=register_form.email.data.lower(),
                            password=hash_and_salted_password)
            db.session.add(new_user)
            db.session.commit()
            flash('Вы успешно зарегистрировались')
            return redirect(url_for("login"))
    return render_template("register.html", form=register_form,
                           error=error, logged_in=current_user.is_authenticated)


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
    return render_template('reset-password.html', form=form)


@app.route('/update/<int:pass_id>', methods=["GET", "POST"])
def update_pass(pass_id):
    pass_to_update = PassTransport.query.get(pass_id)
    update_form = UpdatePassForm()
    if update_form.validate_on_submit():
        pass_to_update.expiry_date = update_form.validation_period.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('update-pass.html', form=update_form,
                           logged_in=current_user.is_authenticated)


@app.route('/delete-pass/<int:pass_id>')
def delete_pass(pass_id):
    pass_to_delete = PassTransport.query.get(pass_id)
    db.session.delete(pass_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/delete-transport/<int:transport_id>')
def delete_transport(transport_id):
    transport_to_delete = PersonalTransport.query.get(transport_id)
    db.session.delete(transport_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)
