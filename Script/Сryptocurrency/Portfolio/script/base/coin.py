import logging
from peewee import TextField, Model, fn
from .sqlite.connectSqlite import ConnectSqlite, ExceptionSelect, ExceptionInsert


class Coin(Model):
    """
    База данных таблица Счета в сейфе
    """
    name = TextField()

    class Meta:
        table_name = 'coin'
        database = ConnectSqlite.get_connect()


class ModelCoin:
    __name_model = 'coin'

    @classmethod
    def __check_coin(cls, name: str) -> bool:
        """
        Проверка есть ли такая монета
        """
        try:
            list_coin = Coin.select(fn.COUNT(Coin.name).alias('count_name')).where(Coin.name == name)
            for sel in list_coin:
                if sel.count_name == 1:
                    logging.warning(f'В таблице {cls.__name_model} уже есть монета {name}')
                    return True  # монета есть
                elif sel.count_name > 1:
                    logging.warning(f'В таблице {cls.__name_model} больше одной монеты {name} = {sel.count_name} шт.')
                    return True  # монеты есть
                return False  # цикл дальше продолжать не надо
            return False  # пустой ответ на запрос - монет нет
        except Exception as err:
            raise ExceptionSelect(cls.__name_model, str(err))

    @classmethod
    def __create_coin(cls, name: str):
        """
        Добавляет монету в базу
        """
        try:
            Coin.create(name=name)
        except Exception as err:
            raise ExceptionInsert(cls.__name_model, str(err))

    @classmethod
    def test_coin(cls, name: str):
        """
        Проверка есть ли такая монета.
        Если монеты нет, создаем.
        """
        logging.info(f'Проверка есть монета: {name}')
        have_coin = cls.__check_coin(name)
        if have_coin:
            return
        cls.__create_coin(name)
