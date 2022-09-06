from . import db
from sqlalchemy import Column, Integer, String, ForeignKey, Date, DateTime
from sqlalchemy.orm import relationship
from flask_login import UserMixin
import jwt
from time import time
from config import ConfigClass

print(ConfigClass.SECRET_KEY)


# -----------------CONFIGURE DB TABLES----------------------
class Settlement(db.Model):
    __tablename__ = "settlements"
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False, unique=True)
    residents = relationship("User", back_populates="settlement")


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    plot_number = Column(String(100))
    first_name = Column(String(100))
    last_name = Column(String(100))
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
            ConfigClass.SECRET_KEY, algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            user_id = jwt.decode(token, ConfigClass.SECRET_KEY,
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

    def get_confirm_email_token(self, expires_in=300):
        return jwt.encode(
            {'confirm_email': self.id, 'exp': time() + expires_in},
            ConfigClass.SECRET_KEY, algorithm='HS256')

    @staticmethod
    def verify_confirm_email_token(token):
        try:
            unconfirmed_user_id = jwt.decode(token, ConfigClass.SECRET_KEY,
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