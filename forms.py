from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, DateField, IntegerField
from wtforms.validators import DataRequired


class NewPassForm(FlaskForm):
    vin = StringField("Номер автомобиля", validators=[DataRequired()])
    validation_period = DateField("Пропуск до", validators=[DataRequired()])
    submit = SubmitField("Отправить")


class UpdatePassForm(FlaskForm):
    validation_period = DateField("Обновить действие пропуска до", validators=[DataRequired()])
    submit = SubmitField("Отправить")


class NewTransportForm(FlaskForm):
    vin = StringField("Номер автомобиля", validators=[DataRequired()])
    submit = SubmitField("Отправить")


class SignInForm(FlaskForm):
    login = StringField("Логин", validators=[DataRequired()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    submit = SubmitField("Вход")


class RegisterForm(FlaskForm):
    first_name = StringField("Имя", validators=[DataRequired()])
    last_name = StringField("Фамилия", validators=[DataRequired()])
    plot_number = IntegerField("Номер участка", validators=[DataRequired()])
    login = StringField("Придумайте логин для входа")
    password = PasswordField("Придумайет пароль", validators=[DataRequired()])
    submit = SubmitField("Зарегистрироваться")
