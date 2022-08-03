import logging
from peewee import DateTimeField, IntegerField, Model, fn
from .sqlite.connectSqlite import ConnectSqlite, ExceptionInsert, ExceptionSelect
from datetime import datetime
from .safelist import Safelist


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

    def __init__(self, id_user: int):
        self._safes_user = None
        self._id_user = id_user

    def __check(self, id_safe: int) -> bool:
        """
        Проверка есть сейф у юзера
        """
        try:
            list_safe = Safeuser.select(fn.COUNT(Safeuser.id).alias('count_safe')).\
                where(Safeuser.id_safe == id_safe,Safeuser.id_user == self._id_user)
            for sel in list_safe:
                if sel.count_safe == 1:
                    logging.warning(f'В таблице {self.__name_model} у ID юзера:{self._id_user} '
                                    f'уже есть ID сейф:{id_safe}')
                    return True  # сейф есть
                elif sel.count_safe > 1:
                    logging.warning(f'В таблице {self.__name_model} у ID юзера:{self._id_user} больше одного '
                                    f'ID сейф:{id_safe} = {sel.count_safe} шт.')
                    return True  # сейфы есть
                return False  # цикл дальше продолжать не надо
            return False  # пустой ответ на запрос - сейфов нет
        except Exception as err:
            raise ExceptionSelect(self.__name_model, str(err))

    def __create(self, id_safe: int) -> int:
        """
        Прикрепление сейфа к юзеру
        :param id_safe: ID сейфа
        """
        try:
            id_safe_user = Safeuser.create(id_safe=id_safe,
                                           id_user=self._id_user)
            logging.info(f'Прикреплен ID сейф юзера:{id_safe_user} id_safe:{id_safe} id_user:{self._id_user}')
            return id_safe_user
        except Exception as err:
            raise ExceptionInsert(self.__name_model, str(err))

    def test(self, id_safe: int):
        """
        Проверка есть ли такой сейф у юзера.
        Если сейфа нет - прикрепляем.
        """
        logging.info(f'Проверка наличия ID сейф:{id_safe} у ID юзер:{self._id_user}')
        have_safe = self.__check(id_safe)
        if have_safe:
            return
        self.__create(id_safe)

    def get_dict(self) -> dict:
        """
        Выгрузить все сейфы юзера
        """
        dict_out = {}
        try:
            print('2525')
            self._safes_user = Safeuser.select(Safeuser.id, Safelist.name).join(Safelist, on=(Safelist.id == Safeuser.id_safe)).where(Safeuser.id_user == self._id_user)
            print(self._safes_user)
            if self._safes_user:
                for sel in self._safes_user:
                    dict_out[sel.id] = sel.safelist.name
                return dict_out
            else:
                logging.warning(f'В таблице {self.__name_model} у ID юзера:{self._id_user} нет сейфов.')
        except Exception as err:
            raise ExceptionSelect(self.__name_model, str(err))
