import logging
from peewee import DateTimeField, IntegerField, DoubleField, Model
from .sqlite.connectSqlite import ConnectSqlite
from datetime import datetime


class EventBank(Model):
    """
    База данных таблица Событий ввода и вывода средств
    """
    id = IntegerField()
    date_time = DateTimeField(default=datetime.now())
    id_cash = IntegerField()
    amount = DoubleField()
    price_avr_fiat = DoubleField()
    fee = DoubleField()

    class Meta:
        table_name = 'event_bank'
        database = ConnectSqlite.get_connect()
