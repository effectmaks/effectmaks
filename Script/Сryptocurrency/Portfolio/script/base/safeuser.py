import logging
from peewee import DateTimeField, IntegerField, Model, fn
from .sqlite.connectSqlite import ConnectSqlite, ExceptionInsert, ExceptionSelect
from datetime import datetime


class Safeuser(Model):
    """
    База данных таблица Сейф.
    Это разные сущности (биржи, кошелки, стейкинги).
    """
    id = IntegerField()
    date_time_create = DateTimeField(default=datetime.now())
    id_safe = IntegerField()
    id_user = IntegerField()

    class Meta:
        table_name = 'safeuser'
        database = ConnectSqlite.get_connect()


class ModelSafeuser:
    __name_model = 'safeuser'

    @classmethod
    def __check(cls, id_user: int, id_safe: int) -> bool:
        """
        Проверка есть сейф у юзера
        """
        try:
            list_safe = Safeuser.select(fn.COUNT(Safeuser.id).alias('count_safe')).where(Safeuser.id_safe == id_safe, Safeuser.id_user == id_user)
            for sel in list_safe:
                if sel.count_safe == 1:
                    logging.warning(f'В таблице {cls.__name_model} у ID юзера:{id_user} уже есть ID сейф:{id_safe}')
                    return True  # сейф есть
                elif sel.count_safe > 1:
                    logging.warning(f'В таблице {cls.__name_model} у ID юзера:{id_user} больше одного '
                                    f'ID сейф:{id_safe} = {sel.count_safe} шт.')
                    return True  # сейфы есть
                return False  # цикл дальше продолжать не надо
            return False  # пустой ответ на запрос - сейфов нет
        except Exception as err:
            raise ExceptionSelect(cls.__name_model, str(err))

    @classmethod
    def __create(cls, id_user: int, id_safe: int) -> int:
        """
        Прикрепление сейфа к юзеру
        :param id_safe: ID сейфа
        :param coin: Монета
        :param amount_buy: Количество купить
        :param price_buy_fiat: Цена покупки
        """
        try:
            id_safe_user = Safeuser.create(id_safe=id_safe,
                                        id_user=id_user)
            logging.info(f'Прикреплен ID сейф юзера:{id_safe_user} id_safe:{id_safe} id_user:{id_user}')
            return id_safe_user
        except Exception as err:
            raise ExceptionInsert(cls.__name_model, str(err))

    @classmethod
    def test(cls, id_user: int, id_safe: int):
        """
        Проверка есть ли такой сейф у юзера.
        Если сейфа нет - прикрепляем.
        """
        logging.info(f'Проверка наличия ID сейф:{id_safe} у ID юзер:{id_user}')
        have_safe = cls.__check(id_user, id_safe)
        if have_safe:
            return
        cls.__create(id_user, id_safe)