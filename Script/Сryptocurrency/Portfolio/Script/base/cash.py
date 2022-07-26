import logging
from peewee import DateTimeField, IntegerField, DoubleField, TextField, Model
from .sqlite.connectSqlite import ConnectSqlite, ExceptionInsert
from datetime import datetime


class Cash(Model):
    """
    База данных таблица Счета в сейфе
    """
    id = IntegerField()
    date_time_update = DateTimeField(default=datetime.now())
    id_safe = IntegerField()
    coin = TextField()
    amount = DoubleField()
    price_avr_fiat = DoubleField()

    class Meta:
        table_name = 'cash'
        database = ConnectSqlite.get_connect()


class ModelCash:

    @classmethod
    def add_cash(cls, id_safe: int, coin: str, amount: float, price_avr_fiat: float):
        try:
            id_cash = Cash.create(id_safe=id_safe,
                                    coin=coin,
                                    amount=amount,
                                    price_avr_fiat=price_avr_fiat)
        except Exception as err:
            raise ExceptionInsert('cash', str(err))


