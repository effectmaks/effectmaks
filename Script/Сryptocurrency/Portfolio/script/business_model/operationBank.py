import datetime
import logging
from telegram_bot.api.telegramApi import ConnectTelebot
from base.safeuser import ModelSafeuser
from base.safelist import Safetypes, ModelSafelist
from base.coin import ModelCoin
from base.cash import ModelCash
from telegram_bot.api.modesWork import ModesWork
from .simpledate import SimpleDate
from .nextfunction import NextFunction


class ExceptionOperationBank(Exception):
    def __init__(self, err_message: str = ''):
        logging.error(err_message)
        super().__init__(err_message)


class OperationBank:
    """
    Операции ввода, вывода и конвертации средств
    """
    def __init__(self, connect_telebot: ConnectTelebot, command_now: str):
        logging.info('Создание объекта OperationBank')
        self._command_now = command_now
        self._connect_telebot = connect_telebot
        self._next_function = NextFunction()
        self._choice_date_time: datetime
        self._choice_safe_type: str
        self._MODE_ADD = 'ДОБАВИТЬ'
        self._dict_safes_user = {}
        self._choice_safe_name: str
        self._choice_id_safe_user: int
        self._TYPE_COIN = 'COIN'
        self._TYPE_USD = 'USD'
        self._choice_coin: str
        self._coin_list = []
        self._choice_amount: float
        self._choice_fee: float

    def work(self, message_str: str):
        if self._next_function.work(message_str):  # функция выполнилась
            return
        if self._command_now == ModesWork.COMMAND_INPUT:
            self._input_date_time_question()
    
    def _input_date_time_question(self):
        """
        Режим вопрос пользователю введите дату и время перевода
        """
        self._connect_telebot.send_text('Введите дату и время:')
        self._next_function.set(self._input_date_time_answer)

    def _input_date_time_answer(self, message_str: str):
        """
        Режим проверки даты и времени
        :param message_str: Ответ юзера
        """
        self._choice_date_time = SimpleDate.convert(message_str)
        self._input_safe_type()

    def _input_safe_type(self):
        """
        Режим  формирование вопроса, на какой тип сейфа хотите пополнить.
        """
        logging.info(f'Режим задать вопрос, какой тип сейфа?')
        list_name: list = Safetypes.get_list()
        self._connect_telebot.view_keyboard('Выберите тип сейфа:', list_name=list_name)
        self._next_function.set(self._input_safe_type_check)

    def _input_safe_type_check(self, message_str: str):
        """
        Режим  проверяет ответ пользователя, по типу сейфа.
        Если правильно выбран, запоминает выбранный тип сейфа.
        :param message_str: Ответ юзера
        """
        logging.info(f'Режим проверить "{message_str}" - это тип?')
        if Safetypes.check(message_str):
            self._choice_safe_type = message_str
            self._input_safe_list()
        else:
            self._connect_telebot.send_text('Выбран неправильный тип сейфа.')
            raise ExceptionOperationBank(f'Выбран не правильный тип сейфа - {message_str}')

    def _input_safe_list(self):
        """
        Режим показать сейфы с типом self._choice_safe_type
        """
        logging.info(f'Режим показать сейфы с типом "{self._choice_safe_type}"')
        safes_dict = ModelSafeuser.get_dict(self._connect_telebot.id_user, type_name=self._choice_safe_type)
        if not safes_dict:
            safes_dict = {}
        safes_dict[self._MODE_ADD] = self._MODE_ADD
        self._dict_safes_user = safes_dict
        self._connect_telebot.view_keyboard('Выберите сейф:', dict_name=safes_dict)
        self._next_function.set(self._input_safe_list_check)

    def _input_safe_list_check(self, message_str: str):
        """
        Проверка какой сейф выбрали с типом self._choice_safe_type.
        Или переход на шаг создания нового сейфа с типом self._choice_safe_type.
        :param message_str: Ответ юзера
        """
        if message_str == self._MODE_ADD:
            self._create_safe_question()
        else:
            id_safe = self._dict_safes_user.get(message_str)
            if id_safe:
                self._choice_safe_name = message_str
                self._choice_id_safe_user = id_safe
                logging.info(f'Выбран сейф ID_safe_user:{self._choice_id_safe_user} name:"{self._choice_safe_name}"')
                self._input_coin_question()
            else:
                self._connect_telebot.send_text(f'Такого сейфа "{message_str}" нет в списке.')
                raise ExceptionOperationBank(f'Пользователь выбрал сейф - "{message_str}", он не из списка.')

    def _create_safe_question(self):
        """
        Вопрос - какое имя сейфа создавать?
        """
        logging.info(f'Режим создания сейфа с типом "{self._choice_safe_type}"')
        self._connect_telebot.send_text(f'Введите название сейфа с типом - "{self._choice_safe_type}":')
        self._next_function.set(self._create_safe_answer)

    def _create_safe_answer(self, message_str: str):
        """
        Создать новый сейф у юзера
        :param message_str: Ответ пользователя
        """
        logging.info(f'Режим проверки названия сейфа "{message_str}"')
        message_str = message_str.upper()
        id_safe_list = ModelSafelist.command_create(message_str, self._choice_safe_type)
        self._choice_id_safe_user = ModelSafeuser.command_create(self._connect_telebot.id_user, id_safe_list)
        self._connect_telebot.send_text(f'Добавлен новый сейф "{message_str}" с типом {self._choice_safe_type}.')
        self._input_coin_question()

    def _input_coin_question(self):
        """
        Выбрать монету
        """
        logging.info(f'Режим вопрос пользователю, выберите монету.')
        coin_list = ModelCash.get_cash_coin(self._choice_id_safe_user)
        if not coin_list:
            coin_list = []
        coin_list.append(self._MODE_ADD)
        self._coin_list = coin_list
        self._connect_telebot.view_keyboard('Выберите монету/валюту:', list_name=self._coin_list)
        self._next_function.set(self._input_coin_answer)

    def _input_coin_answer(self, message_str: str):
        """
        Проверить,монета из списка?
        Иначе добавить.
        :param message_str: Ответ пользователя
        """
        logging.info(f'Режим проверка монеты из списка.')
        if message_str == self._MODE_ADD:
            self._create_coin_question()
        else:
            if message_str in self._coin_list:
                self._choice_coin = message_str
                logging.info(f'Выбрана монета "{self._choice_coin}"')
                self._input_amount_question()
            else:
                self._connect_telebot.send_text(f'Пункта "{message_str}" нет в списке.')
                raise ExceptionOperationBank(f'Пользователь выбрал пункт - "{message_str}", он не из списка.')

    def _create_coin_question(self):
        """
        Режим вопрос - какое имя монеты создавать?
        """
        logging.info(f'Режим создания монеты.')
        coin_list = ModelCoin.get_list()
        self._connect_telebot.view_keyboard('Напишите или выберите монету/валюту:', list_name=coin_list)
        self._next_function.set(self._create_coin_answer)

    def _create_coin_answer(self, message_str: str):
        """
        Создать новую монету
        :param message_str: Ответ пользователя
        """
        logging.info(f'Режим проверки названия монеты "{message_str}"')
        message_str = message_str.upper()
        ModelCoin.command_create(message_str)
        self._choice_coin = message_str
        logging.info(f'Выбрана монета "{self._choice_coin}"')
        self._input_amount_question()

    def _input_amount_question(self):
        """
        Режим вопроса, какой объем пополняется?
        """
        logging.info(f'Режим вопроса объем пополнения')
        self._connect_telebot.send_text(f'Введите объем пополнения:')
        self._next_function.set(self._input_amount_answer)

    def _input_amount_answer(self, message_str: str):
        """
        Режим проверка объема пополнения пользователя
        :param message_str: Ответ пользователя
        :return:
        """
        logging.info(f'Режим проверки объема пополнения')
        amount = self._isfloat(message_str)
        if amount:
            self._choice_amount = amount
            logging.info(f'Выбран объем - {self._choice_amount}')
            self._input_fee_question()
        else:
            self._connect_telebot.send_text('Невозможно преобразовать число.')
            raise ExceptionOperationBank(f'Невозможно преобразовать число - {message_str}')

    def _isfloat(self, value_str: str) -> float:
        try:
            value_str = value_str.replace(',', '.')
            return float(value_str)
        except ValueError:
            pass

    def _input_fee_question(self):
        """
        Режим вопроса, какая комиссия снялась?
        """
        logging.info(f'Режим вопроса комиссия')
        self._connect_telebot.send_text(f'Введите комиссию:')
        self._next_function.set(self._input_fee_answer)

    def _input_fee_answer(self, message_str: str):
        """
        Режим проверка комиссия пользователя
        :param message_str: Ответ пользователя
        :return:
        """
        logging.info(f'Режим проверки комиссии')
        amount = self._isfloat(message_str)
        if amount:
            self._choice_fee = amount
            logging.info(f'Введена комиссия - {self._choice_fee}')
            self._input_comment_question()
        else:
            self._connect_telebot.send_text('Невозможно преобразовать число.')
            raise ExceptionOperationBank(f'Невозможно преобразовать число - {message_str}')

    def _input_comment_question(self):
        """
        Режим вопроса, введите комментарий
        """
        logging.info(f'Режим ввода комментария')
        self._connect_telebot.send_text(f'Введите комментарий:')
        self._next_function.set(self._input_comment_answer)

    def _input_comment_answer(self, message_str: str):
        """
        Проверка комментария
        :param message_str: Ответ пользователя
        :return:
        """
        logging.info(f'Режим проверки комментария')
        self._choice_comment = message_str
        logging.info(f'Выбран комментарий - "{self._choice_comment}"')
        self._input_create_task()

    def _input_create_task(self):
        """
        Создание задания на создание счета юзера
        """
        logging.info(f'Создание задания на создание счета юзера')
        self._connect_telebot.send_text(f'Временный стоп')