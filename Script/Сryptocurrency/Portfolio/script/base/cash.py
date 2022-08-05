import logging
from peewee import DateTimeField, IntegerField, DoubleField, TextField, Model
from .sqlite.connectSqlite import ConnectSqlite, ExceptionInsert, ExceptionSelect
from business_model.simpledate import SimpleDate


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

    class Meta:
        table_name = 'cash'
        database = ConnectSqlite.get_connect()


class ModelCash:
    __name_model = 'cash'

    @classmethod
    def add(cls, id_safe: int, date_time_str: str, coin: str, amount_buy: float, price_buy_fiat: float) -> int:
        """
        Добавление счета покупки/конвертирование монеты(средства).
        Исключения: конвертации даты, добавления записи.
        :param id_safe: ID сейфа
        :param date_time_str: Дата и время добавления
        :param coin: Монета
        :param amount_buy: Количество купить
        :param price_buy_fiat: Цена покупки
        """
        logging.info(
                f'Добавить счет id_safe:{id_safe} date_time:{date_time_str} coin:{coin} amount_buy:{amount_buy} '
                f'price_buy_fiat:{price_buy_fiat}')
        date_time_obj = SimpleDate.convert(date_time_str)  # Вызывает исключение при неправильной конвертации
        try:
            id_cash = Cash.create(id_safe=id_safe,
                                  date_time=date_time_obj,
                                  coin=coin,
                                  amount_buy=amount_buy,
                                  price_buy_fiat=price_buy_fiat)
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
                logging.warning(f'В таблице {cls.__name_model} у сейфа ID:{id_safe_user} не было никогда монет.')
        except Exception as err:
            raise ExceptionSelect(cls.__name_model, str(err))
