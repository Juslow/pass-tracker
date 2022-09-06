import os

DB_NAME = 'transport-pass.db'


class ConfigClass(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    ADMIN_MAIL = os.environ.get('ADMIN_MAIL')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')
    SECURITY_MAIL = os.environ.get('SECURITY_MAIL')
    SECURITY_PASSWORD = os.environ.get('SECURITY_PASSWORD')

    uri = os.getenv("DATABASE_URL")  # or other relevant config var
    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    # rest of connection code using the connection string `uri`
    SQLALCHEMY_DATABASE_URI = uri

    # SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False