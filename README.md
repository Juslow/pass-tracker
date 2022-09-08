# Pass tracker Flask Web-application
## General Information
The application is used for tracking and controlling access to private residential territory. It is implemented using Flask and Heroku.
The SQAlchemy library was used to work with databases. 
SQLite database was used during testing, and after deployment on Heroku, PostgreSQL (Heroku Postgre) was connected.  
The application allows for registration, authentication, as well as features for changing user data (changing the password and parameters of added passes).

Application functions:
- New user registration;
- User authentication;
- Restore user password;
- Adding/editing/deleting/viewing passes for entry to private residential areas;
- Separate account for the security guard, allowing to view active passes for all residents;

## Installation
The `requirements.txt` file contains necessary extensions and frameworks.

## Setting up the application
The application requires a number of parameters to be set in the `config.py` file, such as administrator mail, password, etc.
The file contains the SMTP server settings for working with Gmail.



# Pass tracker Flask Веб-приложене 
## Общие сведения
Веб-приложение позволяет отслеживать и контролировать доступ для въезда на частную жилую территорию.
Приложение реализовано с помощью Flask и Heroku.
Для работы с базами данных использовалась библиотека SQAlchemy. 
При тестировании применялась база данных SQLite, а после развертывания на Heroku была подключена PostgreSQL (Heroku Postgre).  
Приложение позволяет выполнять регистрацию, аутентификацию, а также функции по изменению данных пользователя (смена пароля, изменение параметров добавленных пропусков).

Функции приложения:
- Регистрация нового пользователя;
- Аутентификация пользователя;
- Восстановление пароля пользователя;
- Добавление/редактирование/удаление/просмотр пропусков для въезда на частную жилую территорию;
- Отдельный личный кабинет для охраника, позволяющий просматривать активные пропуска всех жильцов;

## Установка
В файле `requirements.txt` указаны необходимые расширения и фреймворки.

## Настройка приложения
Для работы приложения потребуется задать ряд параметров в файле `config.py`, такие как почта администратора, пароль и т.п.
В файле прописаны настройки SMTP сервера для работы с Gmail.
