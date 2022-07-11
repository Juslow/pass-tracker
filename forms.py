from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, DateField, IntegerField, SelectField, DateTimeField
from wtforms.validators import DataRequired, Length, EqualTo, Email, Optional
from datetime import datetime

PLOT_NUMBER_CHOICES = ['22.1', '22.2', '23', '24', '25', '26', '27', '28',
                       '29', '30', '31', '32', '33', '34', '35', '36', '37']
SETTLEMENT_CHOICES = [('1', 'СНТ "Новово-2"')]


def taxi_call_intervals():
    call_intervals = []
    for i in range(0, 12, 2):
        now = datetime.today().hour
        from_hour = now + i
        to_hour = now + i + 2
        if to_hour >= 24:
            to_hour -= 24
        if from_hour >= 24:
            from_hour -= 24
        call_intervals.append((f'{to_hour}', f'{from_hour}:00 - {to_hour}:00'))
    return call_intervals


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