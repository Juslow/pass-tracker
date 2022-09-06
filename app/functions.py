import datetime as dt
from . import db
from .models import TaxiPass, TemporaryPass, UnconfirmedUser


def delete_outdated_passes(days=2):
    """Deletes outdated taxi passes and transport passes in defined amount of days after its' expiration (var:days).
    The default expiration time is 2 days."""
    today = dt.date.today()
    taxi_list = TaxiPass.query.all()
    temporary_passes = TemporaryPass.query.all()
    for transport in temporary_passes:
        expiry_date = transport.expiry_date
        if today - expiry_date > dt.timedelta(days=days):
            db.session.delete(transport)
            db.session.commit()
    for taxi in taxi_list:
        expiration_time = dt.time(hour=taxi.access_time)
        if expiration_time < dt.datetime.today().time():
            db.session.delete(taxi)
            db.session.commit()


def delete_unconfirmed_users(minutes=5):
    """Deletes users who didn't confirm their emails after defined number of minutes.
    The default expiration time is 5 minutes"""
    unconfirmed_users = UnconfirmedUser.query.all()
    for user in unconfirmed_users:
        if dt.datetime.now() - user.time_msg_sent > dt.timedelta(minutes=minutes):
            db.session.delete(user)
            db.session.commit()


def taxi_call_intervals():
    call_intervals = []
    for i in range(0, 12, 2):
        now = dt.datetime.today().hour
        from_hour = now + i
        to_hour = now + i + 2
        if to_hour >= 24:
            to_hour -= 24
        if from_hour >= 24:
            from_hour -= 24
        call_intervals.append((f'{to_hour}', f'{from_hour}:00 - {to_hour}:00'))
    return call_intervals

