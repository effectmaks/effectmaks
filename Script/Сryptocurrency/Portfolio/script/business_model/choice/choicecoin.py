import logging
from enum import Enum
from typing import Dict

from base.models.cash import ModelCash
from base.models.coin import ModelCoin
from business_model.helpers.nextfunction import NextFunction
from business_model.helpers.questionYesNo import QuestionYesNo
from telegram_bot.api.telegramApi import ConnectTelebot, MessageType


class ExceptionChoiceCoin(Exception):
    def __init__(self, err_message: str = ''):
        logging.error(f'Класс {ExceptionChoiceCoin.__name__} - {err_message}')
        super().__init__(err_message)


class ModesChoiceCoin(Enum):
    ADD = 'ADD'
    VIEW = 'VIEW'


class ChoiceCoin:
    def __init__(self, connect_telebot: ConnectTelebot, id_safe_user: int, message: str,
                 mode_work: ModesChoiceCoin):
        self._connect_telebot = connect_telebot
        self._next_function = NextFunction(ChoiceCoin.__name__)
        self._next_function.set(self._input_coin_question)  # первое что выполнит скрипт
        self._id_safe_user: int = id_safe_user
        self._mode_work = mode_work
        self._result_coin: str = ""
        self._MODE_ADD = 'ДОБАВИТЬ'
        self._message_str = message
        self._question_yes_no: QuestionYesNo
        self._coin_dict: Dict

    def _input_coin_question(self):
        """
        Выбрать монету
        """
        logging.info(f'Режим вопрос пользователю, выберите монету.')
        coin_dict = ModelCash.get_cash_coin(self._id_safe_user)
        if not coin_dict:
            coin_dict = {}
        if self._mode_work == ModesChoiceCoin.ADD:
            coin_dict[self._MODE_ADD] = self._MODE_ADD
        if not coin_dict and self._mode_work == ModesChoiceCoin.VIEW:
            self._connect_telebot.send_text('В этом сейфе нет счетов.')
            raise ExceptionChoiceCoin(f'В этом сейфе id_safe_user {self._id_safe_user} нет счетов.')
        self._coin_dict = coin_dict
        self._connect_telebot.view_keyboard(self._message_str, dict_view=self._coin_dict, type_message=MessageType.KEY)
        self._next_function.set(self._input_coin_answer)

    def _input_coin_answer(self):
        """
        Проверить,монета из списка?
        Иначе добавить.
        """
        logging.info(f'Режим проверка монеты из списка.')
        if self._connect_telebot.message == self._MODE_ADD and self._mode_work == ModesChoiceCoin.ADD:
            self._create_coin_question()
        else:
            if self._connect_telebot.message in self._coin_dict.keys():
                self._result_coin = self._connect_telebot.message
                logging.info(f'Выбрана монета "{self._result_coin}"')
            else:
                logging.info(f'Выбрана монета не из списка"')
                self._question_yes_no = QuestionYesNo(self._connect_telebot, "Не выбран пункт из списка.")
                self._wait_answer_repeat()

    def _wait_answer_repeat(self):
        b_working = self._question_yes_no.work()
        if b_working:
            self._next_function.set(self._wait_answer_repeat)
            return
        result: bool = self._question_yes_no.result
        if result:
            self._input_coin_question()
        else:
            raise ExceptionChoiceCoin('Пользователь отказался выбирать монету из списка.')

    def _create_coin_question(self):
        """
        Режим вопрос - какое имя монеты создавать?
        """
        logging.info(f'Режим создания монеты.')
        coin_list = ModelCoin.get_list()
        self._connect_telebot.view_keyboard('Выберите  или напишите монету/валюту:', list_view=coin_list)
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