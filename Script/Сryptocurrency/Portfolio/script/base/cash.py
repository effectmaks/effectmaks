import logging
from peewee import DateTimeField, IntegerField, DoubleField, TextField, Model
from .sqlite.connectSqlite import ConnectSqlite, ExceptionInsert, ExceptionSelect, ExceptionDelete
from datetime import datetime

class Cash(Model):
    """
    База данных таблица Счета в сейфе.
    """
    id = IntegerField()
    date_time = DateTimeField()
    id_safe_user = IntegerField()
    coin = TextField()
    amount_buy = DoubleField(default=0)
    price_buy_fiat = DoubleField(default=0)
    id_task = IntegerField()

    class Meta:
        table_name = 'cash'
        database = ConnectSqlite.get_connect()


class ModelCash:
    __name_model = 'cash'

    @classmethod
    def add(cls, id_safe_user: int = 0, date_time: datetime = None, coin: str = "", amount_buy: float = 0,
                 price_buy_fiat: float = 0, id_task: int = 0) -> int:
        """
        Добавление счета покупки/конвертирование монеты(средства).
        Исключения: конвертации даты, добавления записи.
        :rtype: object
        :param id_safe_user: ID сейфа
        :param date_time: Дата и время добавления
        :param coin: Монета
        :param amount_buy: Количество купить
        :param price_buy_fiat: Цена покупки
        :param id_task: ID задания
        """
        logging.info(
            f'Добавить счет id_safe_user:{id_safe_user}, date_time:{date_time}, coin:{coin}, amount_buy:{amount_buy}, '
            f'price_buy_fiat:{price_buy_fiat}, _id_task:{id_task}')
        try:
            id_cash = Cash.create(id_safe_user=id_safe_user,
                                  date_time=date_time,
                                  coin=coin,
                                  amount_buy=amount_buy,
                                  price_buy_fiat=price_buy_fiat,
                                  id_task=id_task)
            logging.info(f'Новый счет ID:{id_cash}')
            return id_cash
        except Exception as err:
            raise ExceptionInsert(cls.__name_model, str(err))

    @classmethod
    def get_cash_coin(cls, id_safe_user: int) -> list:
        """
        Выгрузить все монеты счетов юзера у сейфа
        """
        list_out = []
        try:
            cashes_user = Cash.select(Cash.coin).distinct().where(Cash.id_safe_user == id_safe_user)
            if cashes_user:
                for cash in cashes_user:
                    list_out.append(cash.coin)
                return list_out
            else:
                logging.info(f'В таблице {cls.__name_model} у сейфа ID:{id_safe_user} не было никогда монет.')
        except Exception as err:
            raise ExceptionSelect(cls.__name_model, str(err))

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
            cash_list = Cash.select().where(Cash.id_task == id_task)
            for cash in cash_list:
                logging.info(f'Будет удалено в таблице {cls.__name_model}: счет id_safe:{cash.id_safe_user}, '
                                f'date_time:{cash.date_time}, coin:{cash.coin}, amount_buy:{cash.amount_buy}, '
                                f'price_buy_fiat:{cash.price_buy_fiat}')
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
            command_delete = Cash.delete().where(Cash.id_task == id_task)
            count = command_delete.execute()
            logging.info(f'Удалены записи в кол-ве - {count} шт.')
        except Exception as err:
            raise ExceptionDelete(cls.__name_model, str(err))



