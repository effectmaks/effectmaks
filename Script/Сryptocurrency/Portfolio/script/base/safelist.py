import logging
from peewee import TextField, IntegerField, Model, fn
from .sqlite.connectSqlite import ConnectSqlite, ExceptionSelect, ExceptionInsert


class Safetypes:
    EXCHANGE = 'EXCHANGE'
    WALLET = 'WALLET'
    STAKING = 'STAKING'

    @classmethod
    def get_list(cls) -> list:
        """
        :return: Лист с типами сейфов.
        """
        return [cls.EXCHANGE, cls.WALLET, cls.STAKING]

    @classmethod
    def check(cls, type_name: str) -> bool:
        if type_name in [cls.EXCHANGE, cls.WALLET, cls.STAKING]:
            return True
        logging.warning(f'В Safetypes нет типа: {type_name}.')


class Safelist(Model):
    """
    База данных таблица разновидностей сейфов
    """
    id = IntegerField()
    name = TextField()
    type = TextField()

    class Meta:
        table_name = 'safelist'
        database = ConnectSqlite.get_connect()


class ModelSafelist:
    __name_model = 'safelist'

    @classmethod
    def __check(cls, name_safe: str, type_safe: str) -> int:
        """
        Проверка есть сейф
        """
        try:
            list_safe = Safelist.select().where(Safelist.name == name_safe, Safelist.type == type_safe)
            for sel in list_safe:
                logging.info('Сейф уже есть в базе')
                return sel.id
            logging.info('Нет такого сейфа')
        except Exception as err:
            raise ExceptionSelect(cls.__name_model, str(err))

    @classmethod
    def __create(cls, name_safe: str, type_safe: str) -> int:
        """
        Прикрепление сейфа к юзеру
        :param id_safe: ID сейфа
        """
        try:
            id_safe = Safelist.create(name=name_safe, type=type_safe)
            logging.info(f'Создан сейф name:{name_safe}, type:{type_safe} в базе')
            return id_safe
        except Exception as err:
            raise ExceptionInsert(cls.__name_model, str(err))

    @classmethod
    def command_create(self, name_safe: str, type_safe: str) -> int:
        """
        Проверка есть ли такой сейф в списке.
        Если сейфа нет - создаем.
        """
        logging.info(f'Проверка наличия name_safe:{name_safe}, type_safe:{type_safe} в базе')
        id_safe = self.__check(name_safe, type_safe)
        if id_safe:
            return id_safe
        else:
            return self.__create(name_safe, type_safe)
