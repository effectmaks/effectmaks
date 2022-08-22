import logging
from datetime import datetime
from decimal import Decimal

from peewee import DateTimeField, IntegerField, DoubleField, Model
from base.sqlite.connectSqlite import ConnectSqlite, ExceptionInsert, ExceptionSelect, ExceptionDelete


class CashSell(Model):
    """
    База данных таблица Счета продажи в сейфе.
    """
    id = IntegerField()
    date_time = DateTimeField()
    id_cash = IntegerField()
    id_task = IntegerField()
    amount_sell = DoubleField(default=0)
    price_sell = DoubleField(default=0)

    class Meta:
        table_name = 'cashsell'
        database = ConnectSqlite.get_connect()


class ModelCashSell:
    __name_model = 'cashsell'

    @classmethod
    def add(cls, id_task: int, date_time: datetime, id_cash: int, amount_sell: Decimal, price_sell: float = 0) -> int:
        """
        Снятие/конвертирование со счета монеты(средства).
        Исключения: конвертации даты, добавления записи.
        :param id_task: ID задания
        :param id_cash: Счет снятия средств
        :param date_time: Дата и время добавления
        :param amount_sell: Количество купить
        :param price_sell: Цена покупки
        """
        logging.info(
                f'Добавить списание со счета id_task:{id_task}, date_time:{date_time} id_cash:{id_cash} amount_sell:{amount_sell} '
                f'price_sell:{price_sell}')
        try:
            id_cash_sell = CashSell.create(id_task=id_task,
                                           date_time=date_time,
                                           id_cash=id_cash,
                                           amount_sell=amount_sell,
                                           price_sell=price_sell)
            logging.info(f'Ссылка на счет продажи ID:{id_cash_sell}')
            return id_cash_sell
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
        :param id_task: ID задания
        :return: True - есть что удалить.
        """
        must_delete: bool = False
        logging.info('Показать, что будет удалено.')
        try:
            cash_list = CashSell.select().where(CashSell.id_task == id_task)
            for cash in cash_list:
                logging.info(f'Будет удалено в таблице {cls.__name_model}: счет id:{cash.id}, '
                                f'date_time:{cash.date_time}, id_cash:{cash.id_cash}, amount_sell:{cash.amount_sell}, '
                                f'price_sell:{cash.price_sell}')
                must_delete = True
            return must_delete
        except Exception as err:
            raise ExceptionSelect(cls.__name_model, str(err))

    @classmethod
    def _must_delete_task(cls, id_task: int = 0):
        """
        Удалить записи - Task.status == TaskStatus.RUN
        :param id_task: ID задания
        """
        logging.info('Удалить записи со статусом TaskStatus.RUN.')
        try:
            command_delete = CashSell.delete().where(CashSell.id_task == id_task)
            count = command_delete.execute()
            logging.info(f'Удалены записи в кол-ве - {count} шт.')
        except Exception as err:
            raise ExceptionDelete(cls.__name_model, str(err))
