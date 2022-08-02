import logging
from peewee import DateTimeField, IntegerField, DoubleField, TextField, Model
from .sqlite.connectSqlite import ConnectSqlite, ExceptionInsert
from business_model.simpledate import SimpleDate


class EventBank(Model):
    """
    База данных таблица Событий ввода и вывода средств
    """
    id = IntegerField()
    date_time = DateTimeField()
    id_cash_buy = IntegerField()
    id_cash_sell = IntegerField()
    comment = TextField()
    fee = DoubleField()
    id_task = IntegerField()
    type = TextField()

    class Meta:
        table_name = 'eventbank'
        database = ConnectSqlite.get_connect()


class ModelEventBank:
    __name_model = 'eventbank'

    @classmethod
    def add(cls, id_task: int, type: str, date_time_str: str, id_cash_buy: int = 0,
            id_cash_sell: int = 0, fee: float = '', comment: str = '') -> int:
        """
        Добавление события банка. Конвертация, ввод и вывод из системы.
        Исключения: конвертации даты, добавления записи.
        :param id_task:
        :param type:
        :param date_time_str:
        :param id_cash_buy:
        :param id_cash_sell:
        :param comment:
        :param fee:
        :return:
        """

        logging.info(
            f'Добавление события банка id_task:{id_task} type:{type} '
            f'date_time_str:{date_time_str} id_cash_buy:{id_cash_buy} id_cash_sell:{id_cash_sell} '
            f'fee:{fee} comment:{comment}')
        date_time_obj = SimpleDate.convert(date_time_str)  # Вызывает исключение при неправильной конвертации
        try:
            id_event = EventBank.create(id_task=id_task,
                                        type=type,
                                        date_time=date_time_obj,
                                        id_cash_buy=id_cash_buy,
                                        id_cash_sell=id_cash_sell,
                                        fee=fee,
                                        comment=comment)
            logging.info(f'Новое событие банка ID:{id_event}')
            return id_event
        except Exception as err:
            raise ExceptionInsert(cls.__name_model, str(err))
