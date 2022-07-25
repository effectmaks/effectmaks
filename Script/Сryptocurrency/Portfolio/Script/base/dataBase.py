import logging
from peewee import SqliteDatabase, DateTimeField, DateField, IntegerField, TextField, DoubleField, Model, fn
from datetime import datetime
from typing import List

conn = SqliteDatabase('db.sqlite3')


class Cash(Model):
    """
    База данных таблица Счета в сейфе
    """
    id = IntegerField()
    date_time_update = DateTimeField(default=datetime.now())
    id_safe = IntegerField()
    id_coin = IntegerField()
    amount = DoubleField()
    price_avr_fiat = DoubleField()

    class Meta:
        table_name = 'cash'
        database = conn


class Event_bank(Model):
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
        database = conn

