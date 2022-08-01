import logging
from peewee import DateTimeField, IntegerField, DoubleField, TextField, Model
from .sqlite.connectSqlite import ConnectSqlite, ExceptionInsert
from business_model.simpledate import SimpleDate


class CashSell(Model):
    """
    База данных таблица Счета продажи в сейфе.
    """
    id = IntegerField()
    date_time = DateTimeField()
    id_cash = IntegerField()
    amount_sell = DoubleField(default=0)
    price_sell_fiat = DoubleField(default=0)

    class Meta:
        table_name = 'cashsell'
        database = ConnectSqlite.get_connect()


class ModelCashSell:
    __name_model = 'cashsell'

    @classmethod
    def add(cls, id_safe: int, date_time_str: str, id_cash: int, amount_sell: float, price_sell_fiat: float) -> int:
        """
        Снятие/конвертирование со счета монеты(средства).
        Исключения: конвертации даты, добавления записи.
        :param id_safe: ID сейфа
        :param date_time_str: Дата и время добавления
        :param coin: Монета
        :param amount_buy: Количество купить
        :param price_buy_fiat: Цена покупки
        """
        logging.info(
                f'Добавить счет id_safe:{id_safe} date_time:{date_time_str} id_cash:{id_cash} amount_sell:{amount_sell} '
                f'price_sell_fiat:{price_sell_fiat}')
        date_time_obj = SimpleDate.convert(date_time_str)  # Вызывает исключение при неправильной конвертации
        try:
            id_cash_sell = CashSell.create(id_safe=id_safe,
                                  date_time=date_time_obj,
                                  id_cash=id_cash,
                                  amount_sell=amount_sell,
                                  price_sell_fiat=price_sell_fiat)
            logging.info(f'Ссылка на счет продажи ID:{id_cash_sell}')
            return id_cash_sell
        except Exception as err:
            raise ExceptionInsert(cls.__name_model, str(err))
