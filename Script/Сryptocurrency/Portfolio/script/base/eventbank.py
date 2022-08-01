import logging
from peewee import DateTimeField, IntegerField, DoubleField, Model
from .sqlite.connectSqlite import ConnectSqlite, ExceptionInsert
from business_model.simpledate import SimpleDate


class EventBank(Model):
    """
    База данных таблица Событий ввода и вывода средств
    """
    id = IntegerField()
    date_time = DateTimeField()
    amount = DoubleField()
    price_avr_fiat = DoubleField()
    fee = DoubleField()
    id_cash = IntegerField()
    id_cash_sell = IntegerField()

    class Meta:
        table_name = 'event_bank'
        database = ConnectSqlite.get_connect()


class ModelEventBank:
    __name_model = 'cash'

    @classmethod
    def add(cls, id_safe: int, date_time_str: str, amount: float, price_avr_fiat: float, id_cash: int = 0,
            id_cash_sell: int = 0) -> int:
        """
        Добавление события банка.
        Исключения: конвертации даты, добавления записи.
        :param id_safe:
        :param date_time_str:
        :param amount:
        :param price_avr_fiat:
        :param id_cash:
        :param id_cash_sell:
        :return:
        """

        logging.info(
            f'Добавление события банка id_safe:{id_safe} date_time:{date_time_str} '
            f'amount:{amount} price_avr_fiat:{price_avr_fiat} id_cash:{id_cash} id_cash_sell:{id_cash_sell}')
        date_time_obj = SimpleDate.convert(date_time_str)  # Вызывает исключение при неправильной конвертации
        try:
            id_event = EventBank.create(id_safe=id_safe,
                                        date_time=date_time_obj,
                                        id_cash=id_cash,
                                        id_cash_sell=id_cash_sell,
                                        amount=amount,
                                        price_avr_fiat=price_avr_fiat)
            logging.info(f'Новое событие банка ID:{id_event}')
            return id_event
        except Exception as err:
            raise ExceptionInsert(cls.__name_model, str(err))
