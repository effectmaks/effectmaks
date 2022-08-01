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

    @classmethod
    def create(cls, id_user: int, id_safe: int) -> int:
        """
        Прикрепление сейфа к юзеру
        :param id_safe: ID сейфа
        :param coin: Монета
        :param amount_buy: Количество купить
        :param price_buy_fiat: Цена покупки
        """
        try:
            id_safe_user = Safeuser.create(id_safe=id_safe,
                                        id_user=id_user)
            logging.info(f'Прикреплен ID сейф юзера:{id_safe_user} id_safe:{id_safe} id_user:{id_user}')
            return id_safe_user
        except Exception as err:
            raise ExceptionInsert(cls.__name_model, str(err))