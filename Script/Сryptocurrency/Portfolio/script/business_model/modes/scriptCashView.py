import logging
from typing import Dict

from base.models.cash import ModelCash, CashItem
from telegram_bot.api.telegramApi import ConnectTelebot


class ExceptionScriptCashView(Exception):
    def __init__(self, err_message: str = ''):
        logging.error(f'Класс {ExceptionScriptCashView.__name__} - {err_message}')
        super().__init__(err_message)


class ScriptCashView:
    """
    Операции ввода, вывода и конвертации средств
    """
    def __init__(self, connect_telebot: ConnectTelebot):
        logging.info('Создание объекта ScriptCashView')
        self._connect_telebot = connect_telebot

    def work(self):
        """
        Работа класса
        """
        logging.info('Команда показать все счета')
        try:
            cash_dict: Dict[int, CashItem] = ModelCash.get_cash_user(self._connect_telebot.id_user)
            if not cash_dict:
                self._connect_telebot.send_text('У вас нет счетов.')
                return
            str_out: str = ''
            prev_safe: str = ''
            for id_cash, cash in cash_dict.items():
                if prev_safe != cash.safe_name:
                    if prev_safe != '':
                        self._connect_telebot.send_text(str_out)
                    prev_safe = cash.safe_name
                    str_out = f'💰{cash.safe_name} "{cash.safe_type}"\n'
                str_out = f'{str_out}🔺{cash.coin}: {cash.amount}\n'
            self._connect_telebot.send_text(str_out)
            logging.info('Команда выполнена')
        except Exception as err:
            raise ExceptionScriptCashView(f'Ошибка Команда показать все счета - {str(err)}')


