import logging
from datetime import datetime

from peewee import DateTimeField, IntegerField, DoubleField, TextField, Model

from base.sqlite.connectSqlite import ConnectSqlite, ExceptionInsert, ExceptionSelect, ExceptionDelete


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
    def add(cls, id_task: int, type: str, date_time: datetime = None, id_cash_buy: int = 0,
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
            f'Добавление события банка _id_task:{id_task} type:{type} '
            f'date_time_str:{date_time} id_cash_buy:{id_cash_buy} id_cash_sell:{id_cash_sell} '
            f'fee:{fee} comment:{comment}')

        try:
            id_event = EventBank.create(id_task=id_task,
                                        type=type,
                                        date_time=date_time,
                                        id_cash_buy=id_cash_buy,
                                        id_cash_sell=id_cash_sell,
                                        fee=fee,
                                        comment=comment)
            logging.info(f'Новое событие банка ID:{id_event}')
            return id_event
        except Exception as err:
            raise ExceptionInsert(cls.__name_model, str(err))

    @classmethod
    def delete_task_run(cls, id_task: int = 0):
        """
        Команда удалить все запущенные задания - Task.status == TaskStatus.RUN.
        :param id_user:
        """
        logging.info(f'Команда удалить все запущенные задания из {cls.__name_model}.')
        must_delete: bool = cls._view_delete_task(id_task)
        if must_delete:
            cls._must_delete_task(id_task)
        else:
            logging.info('Удаление не требуется.')

    @classmethod
    def _view_delete_task(cls, id_task: int = 0) -> bool:
        """
        Показать в логировании, что будем удалять - Task.status == TaskStatus.RUN
        :param id_user: ID юзера
        :return: True - есть что удалить.
        """
        must_delete: bool = False
        logging.info('Показать, что будет удалено.')
        try:
            bank_list = EventBank.select().where(EventBank.id_task == id_task)
            for bank in bank_list:
                logging.info(f'Будет удалено в таблице {cls.__name_model}: {bank._id_task} type:{bank.type} '
                    f'date_time_str:{bank.date_time} id_cash_buy:{bank.id_cash_buy} id_cash_sell:{bank.id_cash_sell} '
                    f'fee:{bank.fee} comment:{bank.comment}')
                must_delete = True
            return must_delete
        except Exception as err:
            raise ExceptionSelect(cls.__name_model, str(err))

    @classmethod
    def _must_delete_task(cls, id_task: int = 0):
        """
        Удалить записи - Task.status == TaskStatus.RUN
        :param id_user: ID юзера
        :return: True - есть что удалить.
        """
        logging.info('Удалить записи со статусом TaskStatus.RUN.')
        try:
            command_delete = EventBank.delete().where(EventBank.id_task == id_task)
            count = command_delete.execute()
            logging.info(f'Удалены записи в кол-ве - {count} шт.')
        except Exception as err:
            raise ExceptionDelete(cls.__name_model, str(err))