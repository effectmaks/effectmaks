import logging
from peewee import DateTimeField, IntegerField, Model, fn
from base.sqlite.connectSqlite import ConnectSqlite, ExceptionInsert, ExceptionSelect
from datetime import datetime
from .safelist import Safelist


class ExceptionSafeuser(Exception):
    def __init__(self, name_table: str = '', err_message: str = "", err_script_message: str = ''):
        err_message = f'Ошибка {err_message} в таблице {name_table}'
        logging.error(err_message)
        logging.error(err_script_message)
        super().__init__(err_message)


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
            list_safe = Safeuser.select(fn.COUNT(Safeuser.id).alias('count_safe')).\
                where(Safeuser.id_safe == id_safe, Safeuser.id_user == id_user)
            for sel in list_safe:
                if sel.count_safe == 1:
                    logging.info(f'В таблице {cls.__name_model} у ID юзера:{id_user} '
                                 f'уже есть ID сейф:{id_safe}')
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
        """
        try:
            id_safe_user = Safeuser.create(id_safe=id_safe,
                                           id_user=id_user)
            logging.info(f'Создан id_safe_user:{id_safe_user} id_user:{id_user} id_safe_list:{id_safe} ')
            return id_safe_user
        except Exception as err:
            raise ExceptionInsert(cls.__name_model, str(err))

    @classmethod
    def command_create(cls, id_user: int, id_safe: int) -> int:
        """
        Проверка есть ли такой сейф у юзера.
        Если сейфа нет - прикрепляем.
        """
        logging.info(f'Проверка наличия ID сейф:{id_safe} у ID юзер:{id_user}')
        have_safe = cls.__check(id_user, id_safe)
        if have_safe:
            raise ExceptionSafeuser(cls.__name_model, "Уже была проверка, и сейфа не должно быть!")
        else:
            logging.info("Сейфа нет.")
        return cls.__create(id_user, id_safe)

    @classmethod
    def get_dict(cls, id_user: int, type_name: str, view_no_safe_id: int) -> dict:
        """
        Выгрузить все сейфы юзера
        """
        dict_out = {}
        try:
            safes_user = Safeuser.select(Safeuser.id, Safelist.name)\
                                       .join(Safelist, on=(Safelist.id == Safeuser.id_safe))\
                                       .where(Safeuser.id_user == id_user,
                                              Safelist.type == type_name,
                                              Safeuser.id != view_no_safe_id)\
                                       .order_by(Safelist.name)
            if safes_user:
                for sel in safes_user:
                    dict_out[sel.safelist.name] = sel.id
                return dict_out
            else:
                logging.warning(f'В таблице {cls.__name_model} у ID юзера:{id_user} тип {type_name} нет сейфов.')
        except Exception as err:
            raise ExceptionSelect(cls.__name_model, str(err))
