import logging

from base.models.cash import ModelCash
from base.models.coin import ModelCoin
from business_model.nextfunction import NextFunction
from telegram_bot.api.telegramApi import ConnectTelebot


class ExceptionChoiceCoin(Exception):
    def __init__(self, err_message: str = ''):
        logging.error(f'Класс {ExceptionChoiceCoin.__name__} - {err_message}')
        super().__init__(err_message)


class ChoiceCoin:
    def __init__(self, connect_telebot: ConnectTelebot, id_safe_user: int):
        self._connect_telebot = connect_telebot
        self._next_function = NextFunction(ChoiceCoin.__name__)
        self._next_function.set(self._input_coin_question)  # первое что выполнит скрипт
        self._id_safe_user: int = id_safe_user
        self._result_coin: str = ""
        self._MODE_ADD = 'ДОБАВИТЬ'

    def _input_coin_question(self):
        """
        Выбрать монету
        """
        logging.info(f'Режим вопрос пользователю, выберите монету.')
        coin_list = ModelCash.get_cash_coin(self._id_safe_user)
        if not coin_list:
            coin_list = []
        coin_list.append(self._MODE_ADD)
        self._coin_list = coin_list
        self._connect_telebot.view_keyboard('Выберите монету/валюту:', list_view=self._coin_list)
        self._next_function.set(self._input_coin_answer)

    def _input_coin_answer(self):
        """
        Проверить,монета из списка?
        Иначе добавить.
        """
        logging.info(f'Режим проверка монеты из списка.')
        if self._connect_telebot.message == self._MODE_ADD:
            self._create_coin_question()
        else:
            self._result_coin = self._connect_telebot.message
            logging.info(f'Выбрана монета "{self._result_coin}"')

    def _create_coin_question(self):
        """
        Режим вопрос - какое имя монеты создавать?
        """
        logging.info(f'Режим создания монеты.')
        coin_list = ModelCoin.get_list()
        self._connect_telebot.view_keyboard('Напишите или выберите монету/валюту:', list_view=coin_list)
        self._next_function.set(self._create_coin_answer)

    def _create_coin_answer(self):
        """
        Создать новую монету
        """
        logging.info(f'Режим проверки названия монеты "{self._connect_telebot.message}"')
        message_str = self._connect_telebot.message.upper()
        ModelCoin.command_create(message_str)
        self._result_coin = message_str
        logging.info(f'Выбрана монета "{self._result_coin}"')

    @property
    def result(self) -> str:
        return self._result_coin

    def work(self) -> bool:
        self._next_function.work()
        if not self._result_coin:
            return True