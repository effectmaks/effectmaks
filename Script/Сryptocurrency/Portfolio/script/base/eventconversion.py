import logging
from peewee import DateTimeField, IntegerField, DoubleField, TextField, Model
from .sqlite.connectSqlite import ConnectSqlite, ExceptionInsert
from business_model.simpledate import SimpleDate


class EventConversion(Model):
    """
    База данных таблица событий конвертации средств
    """
    id = IntegerField()
    date_time = DateTimeField()
    id_safe = IntegerField()
    coin_sell = TextField()
    amount_sell = DoubleField()
    coin_buy = TextField()
    amount_buy = DoubleField()
    fee = DoubleField()
    comment = TextField()

    class Meta:
        table_name = 'eventconversion'
        database = ConnectSqlite.get_connect()


class ModelEventConversion:
    __name_model = 'eventconversion'

    @classmethod
    def add(cls, id_safe: int, date_time_str: str, coin_sell: str, amount_sell: float,
            coin_buy: str, amount_buy: float, fee: float, comment: str = '') -> int:
        """
        Добавление события конвертации средства.
        Исключения: конвертации даты, добавления записи.
        :param date_time_str:
        :param id_safe:
        :param coin_sell:
        :param amount_sell:
        :param coin_buy:
        :param amount_buy:
        :param fee:
        :param comment:
        :return:
        """

        logging.info(
            f'Добавление события конвертации id_safe:{id_safe} date_time:{date_time_str} '
            f'coin_sell:{coin_sell} amount_sell:{amount_sell} coin_buy:{coin_buy} '
            f'amount_buy:{amount_buy} fee:{fee} comment:{comment}')
        date_time_obj = SimpleDate.convert(date_time_str)  # Вызывает исключение при неправильной конвертации
        try:
            id_event = EventConversion.create(id_safe=id_safe,
                                        date_time=date_time_obj,
                                        coin_sell=coin_sell,
                                        amount_sell=amount_sell,
                                        coin_buy=coin_buy,
                                        amount_buy=amount_buy,
                                        fee=fee,
                                        comment=comment)
            logging.info(f'Новое событие конвертации ID:{id_event}')
            return id_event
        except Exception as err:
            raise ExceptionInsert(cls.__name_model, str(err))
