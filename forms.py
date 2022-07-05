from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, DateField, IntegerField
from wtforms.validators import DataRequired, Length


class NewPassForm(FlaskForm):
    vin = StringField("Номер автомобиля", validators=[DataRequired("Заполните поле")],
                      description="Например: Е999КН77")
    car_model = StringField("Марка автомобиля", validators=[DataRequired("Заполните поле")],
                            description="Например: BMW, Honda, KIA и т.д.")
    validation_period = DateField("Пропуск до", validators=[DataRequired("Заполните поле")])
    submit = SubmitField("Отправить")


class UpdatePassForm(FlaskForm):
    validation_period = DateField("Обновить действие пропуска до", validators=[DataRequired("Заполните поле")])
    submit = SubmitField("Отправить")


class NewTransportForm(FlaskForm):
    vin = StringField("Номер автомобиля", validators=[DataRequired("Заполните поле")],
                      description="Например: Е999КН77")
    car_model = StringField("Марка автомобиля", validators=[DataRequired("Заполните поле")],
                            description="Например: BMW, Honda, KIA и т.д.")
    submit = SubmitField("Отправить")


class SignInForm(FlaskForm):
    login = StringField("Логин", validators=[DataRequired("Заполните поле")])
    password = PasswordField("Пароль", validators=[DataRequired("Заполните поле")])
    submit = SubmitField("Вход")


class RegisterForm(FlaskForm):
    first_name = StringField("Имя", validators=[DataRequired("Заполните поле")])
    last_name = StringField("Фамилия", validators=[DataRequired("Заполните поле")])
    plot_number = IntegerField("Номер участка", validators=[DataRequired("Заполните поле")])
    login = StringField("Логин для входа в личный кабинет",
                        validators=[DataRequired("Заполните поле"),
                                    Length(4, 10, "Для логина используйте от 4 до 10 символов.")])
    password = PasswordField("Пароль",
                             validators=[DataRequired("Заполните поле"),
                                         Length(min=6, max=16, message="Используйте минимум 6 символов.")],
                             description="Используйте минимум 6 символов.")
    repeat_password = PasswordField("Повторите пароль", validators=[DataRequired("Заполните поле")])
    submit = SubmitField("Зарегистрироваться")


class UserValidationForm(FlaskForm):
    first_name = StringField("Имя", validators=[DataRequired("Заполните поле")])
    last_name = StringField("Фамилия", validators=[DataRequired("Заполните поле")])
    plot_number = IntegerField("Номер участка", validators=[DataRequired("Заполните поле")])
    login = StringField("Логин", validators=[DataRequired("Заполните поле")])
    submit = SubmitField("Далее")


class PasswordResetForm(FlaskForm):
    password = PasswordField("Пароль", validators=[DataRequired("Заполните поле"),
                                                   Length(6, 16, "Используйте минимум 6 символов.")],
                             description="Используйте минимум 6 символов.")
    repeat_password = PasswordField("Повторите пароль", validators=[DataRequired("Заполните поле")])
    submit = SubmitField("Сохранить новый пароль")