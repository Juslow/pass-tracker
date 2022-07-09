from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, DateField, IntegerField
from wtforms.validators import DataRequired, Length, EqualTo, Email


class NewPassForm(FlaskForm):
    vin = StringField("Номер автомобиля", validators=[DataRequired("Заполните поле")])
    car_model = StringField("Марка автомобиля", validators=[DataRequired("Заполните поле")])
    validation_period = DateField("Пропуск до", validators=[DataRequired("Заполните поле")])
    submit = SubmitField("Отправить")


class UpdatePassForm(FlaskForm):
    validation_period = DateField("Обновить действие пропска до", validators=[DataRequired("Заполните поле")])
    submit = SubmitField("Отправить")


class NewTransportForm(FlaskForm):
    vin = StringField("Номер автомобиля", validators=[DataRequired("Заполните поле")])
    car_model = StringField("Марка автомобиля", validators=[DataRequired("Заполните поле")])
    submit = SubmitField("Отправить")


class SignInForm(FlaskForm):
    email = StringField("Электронная почта",
                        validators=[DataRequired("Заполните поле"),
                                    Email("Необходимо ввести электронную почту (например: example@email.com)")])
    password = PasswordField("Пароль", validators=[DataRequired("Заполните поле")])
    submit = SubmitField("Вход")


class RegisterForm(FlaskForm):
    first_name = StringField("Имя", validators=[DataRequired("Заполните поле")])
    last_name = StringField("Фамилия", validators=[DataRequired("Заполните поле")])
    plot_number = IntegerField("Номер участка", validators=[DataRequired("Заполните поле")])
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