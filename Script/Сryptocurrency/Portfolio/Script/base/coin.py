import logging
from peewee import TextField, Model
from .sqlite.connectSqlite import ConnectSqlite, ExceptionSelect
from datetime import datetime


class Coin(Model):
    """
    База данных таблица Счета в сейфе
    """
    name = TextField()

    class Meta:
        table_name = 'coin'
        database = ConnectSqlite.get_connect()


class ModelCoin:

    @classmethod
    def check_coin(cls, name: str) -> Coin:
        """
        Проверка есть ли такая монета
        """
        try:
            list_coin: list = Coin.select().where(Coin.name == name) # проверять количество, если больше 1 ошибка админу
            return True
        except Exception as err:
            raise ExceptionSelect('coin', str(err))