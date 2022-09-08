from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user
from werkzeug.security import generate_password_hash

from . import db, login_manager
from .models import Settlement, User, UnconfirmedUser, PermanentPass, TemporaryPass, TaxiPass
from .forms import NewPassForm, NewTransportForm, UpdatePassForm, AddTaxiForm
from .functions import delete_outdated_passes

import datetime as dt
from datetime import date
from functools import wraps

views = Blueprint('views', __name__)


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


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


# ---------------------Web routes-----------------------
@views.route("/")
def home():
    if current_user.is_authenticated:
        return redirect(url_for('views.transport_list'))
    else:
        return redirect(url_for('auth.login'))


@views.route("/transport-list", methods=["GET", "POST"])
def transport_list():
    delete_outdated_passes(days=2)
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    temporary_passes = TemporaryPass.query.filter_by(plot_owner_id=current_user.id)
    permanent_passes = PermanentPass.query.filter_by(owner_id=current_user.id)
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


@views.route("/new-pass", methods=["GET", "POST"])
def new_pass():
    if not current_user.is_authenticated:
        return redirect(url_for('views.home'))
    error = None
    form = NewPassForm()
    if form.validate_on_submit():
        vin = form.vin.data.upper()
        car_model = form.car_model.data.upper()
        # form.validation_period.data returns amount of days as a string
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
            return redirect(url_for("views.transport_list"))
    return render_template("new-pass.html", form=form, logged_in=current_user.is_authenticated, error=error)


@views.route("/add-transport", methods=["GET", "POST"])
def add_transport():
    if not current_user.is_authenticated:
        return redirect(url_for('views.home'))
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
            return redirect(url_for("views.transport_list"))
    return render_template("add-transport.html", form=form, logged_in=current_user.is_authenticated, error=error)


@views.route("/add-taxi", methods=["GET", "POST"])
def add_taxi():
    if not current_user.is_authenticated:
        return redirect(url_for('views.home'))
    form = AddTaxiForm()
    if form.validate_on_submit():
        vin = form.vin.data.upper()
        car_model = form.car_model.data.upper()
        car_color = form.color.data.upper()
        access_time = form.access_time.data
        new_taxi_pass = TaxiPass(vin=vin,
                                 car_model=car_model,
                                 color=car_color,
                                 plot_owner_id=current_user.get_id(),
                                 access_time=int(access_time))
        db.session.add(new_taxi_pass)
        db.session.commit()
        return redirect(url_for('views.transport_list'))
    return render_template('add-taxi.html', form=form, logged_in=current_user.is_authenticated)


@views.route('/update/<int:pass_id>', methods=["GET", "POST"])
def update_pass(pass_id):
    if not current_user.is_authenticated:
        return redirect(url_for('views.home'))
    pass_to_update = TemporaryPass.query.get(pass_id)
    update_form = UpdatePassForm()
    if update_form.validate_on_submit():
        pass_to_update.expiry_date = dt.date.today() + dt.timedelta(int(update_form.validation_period.data))
        db.session.commit()
        return redirect(url_for('views.transport_list'))
    return render_template('update-pass.html', pass_id=pass_id, form=update_form, pass_to_update=pass_to_update,
                           logged_in=current_user.is_authenticated)


@views.route('/delete-pass/<int:pass_id>')
def delete_pass(pass_id):
    if not current_user.is_authenticated:
        return redirect(url_for('views.home'))
    pass_to_delete = TemporaryPass.query.get(pass_id)
    db.session.delete(pass_to_delete)
    db.session.commit()
    return redirect(url_for('views.transport_list'))


@views.route('/delete-transport/<int:transport_id>')
def delete_transport(transport_id):
    if not current_user.is_authenticated:
        return redirect(url_for('views.home'))
    permanent_pass_to_delete = PermanentPass.query.get(transport_id)
    db.session.delete(permanent_pass_to_delete)
    db.session.commit()
    return redirect(url_for('views.transport_list'))


@views.route('/delete-taxi/<int:taxi_id>')
def delete_taxi(taxi_id):
    if not current_user.is_authenticated:
        return redirect(url_for('views.home'))
    taxi_to_delete = TaxiPass.query.get(taxi_id)
    db.session.delete(taxi_to_delete)
    db.session.commit()
    return redirect(url_for('views.transport_list'))


@views.route('/admin', methods=['GET', 'POST'])
@admin_only
def admin():
    if not current_user.is_authenticated:
        return redirect(url_for('views.home'))
    unconfirmed_users = UnconfirmedUser.query.all()
    users = User.query.all()
    temporary_passes = TemporaryPass.query.all()
    permanent_passes = PermanentPass.query.all()
    taxi_passes = TaxiPass.query.all()
    return render_template('admin.html', users=users, unconfirmed_users=unconfirmed_users,
                           temporary_passes=temporary_passes, permanent_passes=permanent_passes,
                           taxi_passes=taxi_passes, today=date.today(),
                           logged_in=current_user.is_authenticated)


@views.route('/admin/delete-user/<int:user_id>', methods=['GET', 'POST'])
@admin_only
def delete_user(user_id):
    if not current_user.is_authenticated:
        return redirect(url_for('views.home'))
    user_to_delete = User.query.get(user_id)
    db.session.delete(user_to_delete)
    db.session.commit()
    return redirect(url_for('views.admin'))


@views.route('/security', methods=['GET'])
@security_only
def security():
    delete_outdated_passes()
    if not current_user.is_authenticated:
        return redirect(url_for('views.home'))
    temporary_passes = TemporaryPass.query.all()
    permanent_passes = PermanentPass.query.all()
    taxi_passes = TaxiPass.query.all()
    return render_template('security.html', temporary_passes=temporary_passes, permanent_passes=permanent_passes,
                           taxi_passes=taxi_passes, today=date.today(), logged_in=current_user.is_authenticated)
