from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, DateField, IntegerField, SelectField, DateTimeField
from wtforms.validators import DataRequired, Length, EqualTo, Email, Optional
from .functions import taxi_call_intervals

PLOT_NUMBER_CHOICES = [i for i in range(1, 20)]
SETTLEMENT_CHOICES = [('1', 'Коттеджный поселок №1"')]


class NewPassForm(FlaskForm):
    vin = StringField("Номер автомобиля", validators=[DataRequired("Заполните поле")])
    car_model = StringField("Марка автомобиля", validators=[DataRequired("Заполните поле")])
    validation_period = SelectField("Сколько дней будет действовать пропуск?",
                                    validators=[DataRequired("Заполните поле")],
                                    choices=['1', '3', '7', '14'])
    submit = SubmitField("Отправить")


class UpdatePassForm(FlaskForm):
    validation_period = SelectField("Сколько дней будет действовать пропуск?",
                                    validators=[DataRequired("Заполните поле")],
                                    choices=['1', '3', '7', '14'])
    submit = SubmitField("Отправить")


class NewTransportForm(FlaskForm):
    vin = StringField("Номер автомобиля", validators=[DataRequired("Заполните поле")])
    car_model = StringField("Марка автомобиля", validators=[DataRequired("Заполните поле")])
    submit = SubmitField("Отправить")


class AddTaxiForm(FlaskForm):
    vin = StringField("Номер автомобиля", validators=[Optional()])
    car_model = StringField("Марка автомобиля", validators=[Optional()])
    color = StringField("Цвет", validators=[Optional()])
    access_time = SelectField("Во сколько приедет такси?", choices=taxi_call_intervals, validators=[DataRequired()])


class SignInForm(FlaskForm):
    email = StringField("Электронная почта",
                        validators=[DataRequired("Заполните поле"),
                                    Email("Необходимо ввести электронную почту (например: example@email.com)")])
    password = PasswordField("Пароль", validators=[DataRequired("Заполните поле")])
    submit = SubmitField("Вход")


class RegisterForm(FlaskForm):
    first_name = StringField("Имя", validators=[DataRequired("Заполните поле")])
    last_name = StringField("Фамилия", validators=[DataRequired("Заполните поле")])
    settlement = SelectField("Поселок", choices=SETTLEMENT_CHOICES, validators=[DataRequired("Заполните поле")])
    plot_number = SelectField("Номер участка", choices=PLOT_NUMBER_CHOICES, validators=[DataRequired("Заполните поле")])
    email = StringField("Электронная почта",
                        validators=[DataRequired("Заполните поле"),
                                    Email("Необходимо ввести электронную почту (например: example@email.com)")])
    password = PasswordField("Пароль",
                             validators=[DataRequired("Заполните поле"),
                                         Length(min=6, max=16, message="Используйте минимум 6 символов.")])
    repeat_password = PasswordField("Повторите пароль",
                                    validators=[DataRequired("Заполните поле")])
    submit = SubmitField("Зарегистрироваться")


class ResetPasswordRequestForm(FlaskForm):
    email = StringField("Электронная почта",
                        validators=[DataRequired("Заполните поле"),
                                    Email("Необходимо ввести электронную почту (например: example@email.com)")])
    submit = SubmitField("Сбросить пароль")


class PasswordResetForm(FlaskForm):
    password = PasswordField("Пароль", validators=[DataRequired("Заполните поле"),
                                                   Length(6, 16, "Используйте минимум 6 символов.")])
    repeat_password = PasswordField("Повторите пароль",
                                    validators=[DataRequired("Заполните поле"),
                                                EqualTo('password', "Пароли не совпадают")])
    submit = SubmitField("Сохранить новый пароль")
