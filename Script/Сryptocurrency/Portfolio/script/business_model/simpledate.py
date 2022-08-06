import logging
from datetime import datetime


class ExceptionSimpleDate(Exception):
    def __init__(self, err_message: str = ''):
        logging.error(err_message)
        super().__init__(err_message)


class SimpleDate:
    """
    Конвертация даты
    """
    @classmethod
    def convert(cls, date_time_str: str) -> datetime:
        date_time = cls._variant_1(date_time_str)
        if date_time:
            return date_time
        date_time = cls._variant_2(date_time_str)
        if date_time:
            return date_time
        if not date_time:
            raise ExceptionSimpleDate(f'cls:{cls.__name__} Ошибка конвертации даты и времени')

    @classmethod
    def _variant_1(cls, date_time_str: str) -> datetime:
        try:
            template: str = '%d.%m.%y %H.%M.%S'
            return datetime.strptime(date_time_str, template)
        except Exception:
            logging.info(f'cls:{cls.__name__} def:{cls._variant_1.__name__} Ошибка конвертации по шаблону "{template}"')

    @classmethod
    def _variant_2(cls, date_time_str: str) -> datetime:
        try:
            template: str = '%d.%m.%Y %H.%M.%S'
            return datetime.strptime(date_time_str, template)
        except Exception:
            logging.info(f'cls:{cls.__name__} def:{cls._variant_2.__name__} Ошибка конвертации по шаблону "{template}"')

