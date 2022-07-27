import logging
from peewee import DateTimeField, IntegerField, DoubleField, TextField, Model
from .sqlite.connectSqlite import ConnectSqlite, ExceptionInsert
from datetime import datetime


class Cash(Model):
    """
    База данных таблица Счета в сейфе
    """
    id = IntegerField()
    date_time = DateTimeField(default=datetime.now())
    id_safe = IntegerField()
    coin = TextField()
    amount_buy = DoubleField(default=0)
    price_buy_fiat = DoubleField(default=0)

    class Meta:
        table_name = 'cash'
        database = ConnectSqlite.get_connect()


class ModelCash:
    __name_model = 'cash'

    @classmethod
    def add_cash(cls, id_safe: int, coin: str, amount_buy: float, price_buy_fiat: float):
        """
        Добавление счета монеты
        :param id_safe: ID сейфа
        :param coin: Монета
        :param amount_buy: Количество купить
        :param price_buy_fiat: Цена покупки
        """
        try:
            id_cash = Cash.create(id_safe=id_safe,
                        coin=coin,
                        amount_buy=amount_buy,
                        price_buy_fiat=price_buy_fiat)
            logging.info(f'Добавлен счет ID:{id_cash} id_safe:{id_safe} coin:{coin} amount_buy:{amount_buy} '
                         f'price_buy_fiat:{price_buy_fiat}')
        except Exception as err:
            raise ExceptionInsert(cls.__name_model, str(err))


