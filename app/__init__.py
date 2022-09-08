from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from config import ConfigClass, DB_NAME
from flask_mail import Mail
from flask_login import LoginManager
from flask_bootstrap import Bootstrap

db = SQLAlchemy()
mail = Mail()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(__name__ + '.ConfigClass')

    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    Bootstrap(app)

    # Connects routes to app from views.py and auth.py
    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    # Connects db models
    from .models import Settlement, User, UnconfirmedUser, PermanentPass, TemporaryPass, TaxiPass
    create_database(app)

    return app


def create_database(app):
    db.create_all(app=app)
    # if not path.exists('app/' + DB_NAME):
    #     db.create_all(app=app)
    #     print('Created Database!')

