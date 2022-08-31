import logging
from typing import Dict, List
from decimal import Decimal

from peewee import DateTimeField, IntegerField, DoubleField, TextField, Model
from base.sqlite.connectSqlite import ConnectSqlite, ExceptionInsert, ExceptionSelect, ExceptionDelete
from datetime import datetime


class CashItem:
    def __init__(self, coin: str, amount: Decimal, price_buy: Decimal = None, coin_avr: str = "",
                 safe_name: str = "", safe_type: str = "", date_time: str = ""):
        self.coin = coin
        self.amount = None
        if amount:
            self.amount = amount.quantize(Decimal('0.00000001'))
        self.price_buy = None
        if price_buy:
            self.price_buy = price_buy.quantize(Decimal('0.00000001'))
        self.coin_avr = coin_avr
        self.safe_name = safe_name
        self.safe_type = safe_type
        self.date_time = date_time


class Cash(Model):
    """
    База данных таблица Счета в сейфе.
    """
    id = IntegerField()
    date_time = DateTimeField()
    id_safe_user = IntegerField()
    coin = TextField()
    amount_buy = DoubleField(default=0)
    price_buy = DoubleField(default=0)
    id_task = IntegerField()
    coin_avr = TextField()

    class Meta:
        table_name = 'cash'
        database = ConnectSqlite.get_connect()


class ModelCash:
    __name_model = 'cash'

    @classmethod
    def add(cls, id_safe_user: int = 0, date_time: datetime = None, coin: str = "", amount_buy: Decimal = None,
            price_buy: Decimal = None, id_task: int = 0, coin_avr: str = "") -> int:
        """
        Добавление счета покупки/конвертирование монеты(средства).
        Исключения: конвертации даты, добавления записи.
        :param coin_avr:
        :rtype: object
        :param id_safe_user: ID сейфа
        :param date_time: Дата и время добавления
        :param coin: Монета
        :param amount_buy: Количество купить
        :param price_buy: Цена покупки
        :param id_task: ID задания
        """
        logging.info(
            f'Добавить счет id_safe_user:{id_safe_user}, date_time_str:{date_time}, coin:{coin}, amount_buy:{amount_buy}, '
            f'price_buy:{price_buy}, _id_task:{id_task}')
        try:
            id_cash = Cash.create(id_safe_user=id_safe_user,
                                  date_time=date_time,
                                  coin=coin,
                                  amount_buy=amount_buy,
                                  price_buy=price_buy,
                                  coin_avr=coin_avr,
                                  id_task=id_task)
            logging.info(f'Новый счет ID:{id_cash}')
            return id_cash
        except Exception as err:
            raise ExceptionInsert(cls.__name_model, str(err))

    @classmethod
    def delete_task_run(cls, id_task: int = 0):
        """
        Команда удалить все запущенные задания - Task.status == TaskStatus.RUN.
        :param id_task:
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
            cash_list = Cash.select().where(Cash.id_task == id_task)
            for cash in cash_list:
                logging.info(f'Будет удалено в таблице {cls.__name_model}: счет id_safe:{cash.id_safe_user}, '
                             f'date_time_str:{cash.date_time}, coin:{cash.coin}, amount_buy:{cash.amount_buy}, '
                             f'price_buy:{cash.price_buy}')
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
            command_delete = Cash.delete().where(Cash.id_task == id_task)
            count = command_delete.execute()
            logging.info(f'Удалены записи в кол-ве - {count} шт.')
            if count == 0:
                raise ExceptionDelete(cls.__name_model, "Не получилось удалить записи")
        except Exception as err:
            raise ExceptionDelete(cls.__name_model, str(err))

    @classmethod
    def get_cash_coin(cls, id_safe_user: int) -> dict:
        """
        Выгрузить все счета в сейфе
        """
        try:
            logging.info('Запрос Выгрузить все счета в сейфе.')
            dict_out = {}
            connect = ConnectSqlite.get_connect()
            cash_list = connect.execute_sql('select coin, sum(amount) from (select cash.coin, '
                                            '(cash.amount_buy - CASE WHEN sum_cash_sell.amount IS NULL '
                                            'THEN 0 else sum_cash_sell.amount end) as amount '
                                            'from cash left join (select id_cash, sum(amount_sell) as amount '
                                            'from cashsell group by id_cash) as sum_cash_sell '
                                            'on cash.id = sum_cash_sell.id_cash '
                                            'where cash.id_safe_user = {}) as filter_zero '
                                            'where amount <> 0 group by coin order by 1'.
                                            format(id_safe_user))
            if cash_list:
                for cash in cash_list:
                    sum_amount = Decimal(cash[1]).quantize(Decimal("0.00000001"))
                    dict_out[cash[0]] = f'{cash[0]}: {sum_amount}'
                logging.info('Запрос выполнен')
                return dict_out
            else:
                logging.info(f'В таблице {cls.__name_model} у сейфа ID:{id_safe_user} не было никогда монет.')
        except Exception as err:
            raise ExceptionSelect(cls.__name_model, str(err))

    @classmethod
    def dict_amount(cls, id_safe_user: int, filter_coin_view_no: str = '',
                    filter_coin_view: str = '',
                    list_cash_no_view: List[int] = None,
                    filter_cash_date_before: datetime = None) -> Dict:
        """
        Запрос объема все счетов у сейфа
        :param filter_coin_view:
        :param filter_coin_view_no:
        :param id_safe_user: ID сейфа юзера
        :return: Словарь со счетами их названиями объемом и ID
        """
        logging.info('Запрос объема все счетов у сейфа.')
        sql_coin_no_view = ''
        sql_cash_no_view: str = ''
        sql_coin_view = ''
        sql_cash_date_before = ''
        if filter_coin_view_no != '':
            sql_coin_no_view = f'and not cash.coin = "{filter_coin_view_no}"'
        if filter_coin_view != '':
            sql_coin_view = f'and cash.coin = "{filter_coin_view}"'
        if list_cash_no_view != None:
            str_id: str = ''
            str_end: str = ', '
            count = len(list_cash_no_view)
            count_item = 0
            for item in list_cash_no_view:
                count_item += 1
                if count_item == count:
                    str_end = ''
                str_id += str(item) + str_end
            sql_cash_no_view = f'and not cash.id in ({str_id})'
        if filter_cash_date_before != None:
            sql_cash_date_before = f'and cash.date_time_str <= "{filter_cash_date_before}"'
        try:
            dict_out = {}
            connect = ConnectSqlite.get_connect()
            cash_list = connect.execute_sql('select id, coin, amount, price_buy, coin_avr, date_time_str '
                                            'from (select cash.id, cash.coin, (cash.amount_buy - '
                                            'CASE WHEN sum_cash_sell.amount IS NULL '
                                            'THEN 0 else sum_cash_sell.amount end) as amount, '
                                            'cash.price_buy, cash.coin_avr,cash.date_time_str '
                                            'from cash '
                                            'left join (select id_cash, sum(amount_sell) as amount '
                                            'from cashsell group by id_cash) as sum_cash_sell '
                                            'on cash.id = sum_cash_sell.id_cash '
                                            'where cash.id_safe_user = {} {} {} {} {}) '
                                            'as filter_zero where amount <> 0 order by 6,2,4,3'.
                                            format(id_safe_user,
                                                   sql_coin_no_view,
                                                   sql_coin_view,
                                                   sql_cash_no_view,
                                                   sql_cash_date_before))
            for cash in cash_list:
                dict_out[int(cash[0])] = CashItem(coin=cash[1], amount=cls._get_decimal(cash[2]),
                                                  price_buy=cls._get_decimal(cash[3]),
                                                  coin_avr=cash[4], date_time=cash[5])
            logging.info('Запрос выполнен')
            return dict_out
        except Exception as err:
            raise ExceptionSelect(cls.__name_model, str(err))

    @classmethod
    def _get_decimal(cls, amount_in) -> Decimal:
        amount = Decimal('0')
        if amount_in:
            amount = Decimal(amount_in)
        return amount

    @classmethod
    def get_cash_user(cls, id_user: int) -> Dict[int, CashItem]:
        """
        Выгрузить все счета юзера
        """
        try:
            logging.info('Запрос Выгрузить все счета юзера.')
            dict_out: Dict[int, CashItem] = {}
            connect = ConnectSqlite.get_connect()
            cash_list = connect.execute_sql('select id, safe_name, safe_type, coin, sum(amount) as sum_amount '
                                            'from (select cash.id, safelist.name '
                                            'as safe_name, safelist.type as safe_type, cash.coin, (cash.amount_buy - '
                                            'CASE WHEN sum_cash_sell.amount IS NULL THEN 0 '
                                            'else sum_cash_sell.amount end) '
                                            'as amount from cash join safeuser on cash.id_safe_user = safeuser.id '
                                            'and safeuser.id_user = {} join safelist '
                                            'on safelist.id = safeuser.id_safe '
                                            'left join (select id_cash, sum(amount_sell) as amount '
                                            'from cashsell group by id_cash) as sum_cash_sell '
                                            'on cash.id = sum_cash_sell.id_cash) as filter_zero '
                                            'where amount <> 0 group by safe_name, safe_type, coin order by 2,3,4 '.
                                            format(id_user))
            if cash_list:
                for cash in cash_list:
                    dict_out[int(cash[0])] = CashItem(safe_name=cash[1], safe_type=cash[2], coin=cash[3],
                                                      amount=Decimal(cash[4]))
                logging.info('Запрос выполнен.')
                return dict_out
            else:
                logging.info(f'В таблице {cls.__name_model} у юзера ID:{id_user} нет счетов.')
        except Exception as err:
            raise ExceptionSelect(cls.__name_model, str(err))
