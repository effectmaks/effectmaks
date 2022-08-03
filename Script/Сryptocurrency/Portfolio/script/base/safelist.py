import logging
from peewee import TextField, IntegerField, Model, fn
from .sqlite.connectSqlite import ConnectSqlite, ExceptionSelect, ExceptionInsert


class Safetypes:
    EXCHANGE = 'EXCHANGE'
    WALLET = 'WALLET'
    STAKING = 'STAKING'


class Safelist(Model):
    """
    База данных таблица разновидностей сейфов
    """
    id = IntegerField()
    name = TextField()
    safetype = TextField()

    class Meta:
        table_name = 'safelist'
        database = ConnectSqlite.get_connect()
