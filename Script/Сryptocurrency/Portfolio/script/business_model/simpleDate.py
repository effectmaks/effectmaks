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
        try:
            return datetime.strptime(date_time_str, '%d.%m.%y %H:%M:%S')
        except Exception as err:
            raise ExceptionSimpleDate(f'Ошибка конвертации даты и времени {str(err)}')