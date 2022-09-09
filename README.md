# (EN) Pass tracker Flask Web-application
## General Information
Originally this project was created for a particular settlement (that's why it is in Russian). Here I want to share a copy of that application with some adjustments.

The application is used for tracking and controlling access to private residential territory. It is implemented using Flask and Heroku.
The SQAlchemy library was used to work with database. 
SQLite database was applied during testing, and after deployment on Heroku, PostgreSQL (Heroku Postgre) was connected.  
The application allows for registration, authentication, as well as features for changing user data (changing the password and parameters of added passes).

Application functions:
- New user registration;
- User authentication;
- Restore user password;
- Adding/editing/deleting/viewing passes for entry to private residential areas;
- Separate account for the security guard, allowing to view active passes for all residents;

You can try this application in action [here](https://vehicle-pass.herokuapp.com/) by using a test account (if you don't want to register) or by creating a new one.

Test account
```
email: member@example.com
password: password
```
## Installation
The `requirements.txt` file contains necessary extensions and frameworks to run the application.

## Setting up the application
The application requires a number of parameters to be set in `config.py` file, such as administrator mail, password, etc.
The file contains the SMTP server settings for working with Gmail.

Also it's set to work with PostgreSQL, connected via Heroku.
To use it localy on your computer you will need to connect SQLite by uncommenting the following string in `config.py` file
```
SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_NAME}"
```
and commenting 
```
    uri = os.getenv("DATABASE_URL")  # or other relevant config var
    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    # rest of connection code using the connection string `uri`
    SQLALCHEMY_DATABASE_URI = uri
```

# (RU) Pass tracker Flask Веб-приложене 
## Общие сведения
Изначально приложение было разработано для коттеджного поселка,
и я бы хотел поделиться этим проектом с некоторыми внесенными правками для возможности получения обратной связи и дальнейшего развития как Web-разработчик.

Веб-приложение позволяет отслеживать и контролировать доступ для въезда на частную жилую территорию.
Приложение реализовано с помощью Flask и Heroku.
Для работы с базой данных использовалась библиотека SQAlchemy. 
При тестировании применялась база данных SQLite, а после развертывания на Heroku была подключена PostgreSQL (Heroku Postgre).  
Приложение позволяет выполнять регистрацию, аутентификацию, а также функции по изменению данных пользователя (смена пароля, изменение параметров добавленных пропусков).

Функции приложения:
- Регистрация нового пользователя;
- Аутентификация пользователя;
- Восстановление пароля пользователя;
- Добавление/редактирование/удаление/просмотр пропусков для въезда на частную жилую территорию;
- Отдельный личный кабинет для охраника, позволяющий просматривать активные пропуска всех жильцов;

Данное приложение можете опробовать по [ссылке](https://vehicle-pass.herokuapp.com/), используя тестовый аккаунт или пройдя регистрацию как новый пользователь.

Тестовый аккаунт
```
email: member@example.com
password: password
```

## Установка
В файле `requirements.txt` указаны необходимые расширения и фреймворки.

## Настройка приложения
Для работы приложения потребуется задать ряд параметров в файле `config.py`, такие как почта администратора, пароль и т.п.
В файле прописаны настройки SMTP сервера для работы с Gmail.

Также приложение настроено на работу с БД PostgreSQL, подключенной через Heroku.
Чтобы использовать локально на вашем компьютере, нужно подключить SQLite, откомментировав следующую строку в файле `config.py`
```
SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_NAME}"
```
и закомментировав
```
    uri = os.getenv("DATABASE_URL")  # or other relevant config var
    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    # rest of connection code using the connection string `uri`
    SQLALCHEMY_DATABASE_URI = uri
```
