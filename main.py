from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey, Date
from flask_bootstrap import Bootstrap
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from forms import NewPassForm, SignInForm, NewTransportForm, UpdatePassForm, \
    RegisterForm, UserValidationForm, PasswordResetForm
from datetime import date, timedelta
import os

app = Flask(__name__)
# TODO: Secret key should be used in Hiroku later
app.config['SECRET_KEY'] = "lsdfDm93EmpjI8WQm2"
db = SQLAlchemy(app)
Bootstrap(app)

# Connect to DB
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///car-pass.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

login_manager = LoginManager()
login_manager.init_app(app)


# -----------------CONFIGURE DB TABLES----------------------
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    plot_number = Column(Integer, unique=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    login = Column(String(100), unique=True)
    password = Column(String(100))

    personal_transport = relationship("PersonalTransport", back_populates="owner")
    pass_transport = relationship("PassTransport", back_populates="plot_owner")


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


# Delete outdated data from db in 7 days
def delete_outdated_data():
    today = date.today()
    pass_transport = PassTransport.query.all()
    for transport in pass_transport:
        expiry_date = transport.expiry_date
        if (expiry_date - today).days < -7:
            db.session.delete(transport)
            db.session.commit()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


# ---------------------Web routes-----------------------
@app.route("/")
def home():
    delete_outdated_data()
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
        login_name = form.login.data.lower()
        password = form.password.data

        user = User.query.filter_by(login=login_name).first()
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
        login_in_use = User.query.filter_by(login=register_form.login.data).first()
        if user:
            error = 'Для данного участка уже имеется личный кабинет, пожалуйста, нажмите кнопку "войти".'
        elif login_in_use:
            error = "Данный логин уже используется, пожалуйста, придумайте новый."
        elif register_form.password.data != register_form.repeat_password.data:
            error = "Пароли не совпадаеют, пожалуйста, введите еще раз."
        else:
            new_user = User(first_name=register_form.first_name.data.title(),
                            last_name=register_form.last_name.data.title(),
                            plot_number=register_form.plot_number.data,
                            login=register_form.login.data.lower(),
                            password=hash_and_salted_password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for("login"))
    return render_template("register.html", form=register_form,
                           error=error, logged_in=current_user.is_authenticated)


@app.route('/user-validation', methods=["GET", "POST"])
def user_validation():
    error = None
    user_validation_form = UserValidationForm()
    if user_validation_form.validate_on_submit():
        first_name = user_validation_form.first_name.data.title()
        last_name = user_validation_form.last_name.data.title()
        login = user_validation_form.login.data.lower()
        user = User.query.filter_by(plot_number=user_validation_form.plot_number.data).first()
        if user:
            if user.first_name == first_name and user.last_name == last_name and user.login == login:
                return redirect(url_for('password_reset', user_id=user.id))
            else:
                error = 'Введены неправильные данные'
        else:
            error = 'Введены неправильные данные'
    return render_template('user-validation.html', form=user_validation_form,
                           logged_in=current_user.is_authenticated, error=error)


@app.route('/password-reset/<int:user_id>', methods=["GET", "POST"])
def password_reset(user_id):
    error = None
    password_reset_form = PasswordResetForm()
    user_password_reset = User.query.get(user_id)
    if password_reset_form.validate_on_submit():
        if password_reset_form.password.data != password_reset_form.repeat_password.data:
            error = "Пароли не совпадаеют, пожалуйста, введите еще раз."
        else:
            hash_and_salted_password = generate_password_hash(password_reset_form.password.data,
                                                              'pbkdf2:sha256',
                                                              8)
            user_password_reset.password = hash_and_salted_password
            db.session.commit()
            return redirect(url_for('login'))
    return render_template('password-reset.html', form=password_reset_form, error=error)


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
