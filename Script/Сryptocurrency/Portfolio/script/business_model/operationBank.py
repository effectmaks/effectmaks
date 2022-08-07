import logging

from base.cash import ModelCash
from base.coin import ModelCoin
from base.safelist import Safetypes, ModelSafelist
from base.safeuser import ModelSafeuser
from telegram_bot.api.commandsWork import CommandsWork
from telegram_bot.api.telegramApi import ConnectTelebot

from .nextfunction import NextFunction
from .simpledate import SimpleDate
from business_model.taskrule import TaskRule


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
        self._MODE_ADD = 'ДОБАВИТЬ'
        self._dict_safes_user = {}
        self._coin_list = []
        self._task_rule: TaskRule

    def work(self, message_str: str):
        if self._next_function.work(message_str):  # функция выполнилась
            return
        if self._command_now == CommandsWork.COMMAND_INPUT:
            self._task_rule = TaskRule(id_user=self._connect_telebot.id_user, command_type=CommandsWork.COMMAND_INPUT)
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
        self._task_rule.date_time = SimpleDate.convert(message_str)
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
            self._task_rule.safe_type = message_str
            self._input_safe_list()
        else:
            self._connect_telebot.send_text('Выбран неправильный тип сейфа.')
            raise ExceptionOperationBank(f'Выбран не правильный тип сейфа - {message_str}')

    def _input_safe_list(self):
        """
        Режим показать сейфы с типом self._task_rule.safe_type
        """
        logging.info(f'Режим показать сейфы с типом "{self._task_rule.safe_type}"')
        safes_dict = ModelSafeuser.get_dict(self._connect_telebot.id_user, type_name=self._task_rule.safe_type)
        if not safes_dict:
            safes_dict = {}
        safes_dict[self._MODE_ADD] = self._MODE_ADD
        self._dict_safes_user = safes_dict
        self._connect_telebot.view_keyboard('Выберите сейф:', dict_name=safes_dict)
        self._next_function.set(self._input_safe_list_check)

    def _input_safe_list_check(self, message_str: str):
        """
        Проверка какой сейф выбрали с типом self._task_rule.safe_type.
        Или переход на шаг создания нового сейфа с типом self._task_rule.safe_type.
        :param message_str: Ответ юзера
        """
        if message_str == self._MODE_ADD:
            self._create_safe_question()
        else:
            id_safe = self._dict_safes_user.get(message_str)
            if id_safe:
                self._task_rule.safe_name = message_str
                self._task_rule.id_safe_user = id_safe
                logging.info(f'Выбран сейф ID_safe_user:{self._task_rule.id_safe_user} name:"{self._task_rule.safe_name}"')
                self._input_coin_question()
            else:
                self._connect_telebot.send_text(f'Такого сейфа "{message_str}" нет в списке.')
                raise ExceptionOperationBank(f'Пользователь выбрал сейф - "{message_str}", он не из списка.')

    def _create_safe_question(self):
        """
        Вопрос - какое имя сейфа создавать?
        """
        logging.info(f'Режим создания сейфа с типом "{self._task_rule.safe_type}"')
        self._connect_telebot.send_text(f'Введите название сейфа с типом - "{self._task_rule.safe_type}":')
        self._next_function.set(self._create_safe_answer)

    def _create_safe_answer(self, message_str: str):
        """
        Создать новый сейф у юзера
        :param message_str: Ответ пользователя
        """
        logging.info(f'Режим проверки названия сейфа "{message_str}"')
        message_str = message_str.upper()
        id_safelist = ModelSafelist.command_create(message_str, self._task_rule.safe_type)
        self._task_rule.id_safe_user = ModelSafeuser.command_create(self._connect_telebot.id_user, id_safelist)
        self._connect_telebot.send_text(f'Добавлен новый сейф "{message_str}" с типом {self._task_rule.safe_type}.')
        self._input_coin_question()

    def _input_coin_question(self):
        """
        Выбрать монету
        """
        logging.info(f'Режим вопрос пользователю, выберите монету.')
        coin_list = ModelCash.get_cash_coin(self._task_rule.id_safe_user)
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
                self._task_rule.coin = message_str
                logging.info(f'Выбрана монета "{self._task_rule.coin}"')
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
        self._task_rule.coin = message_str
        logging.info(f'Выбрана монета "{self._task_rule.coin}"')
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
            self._task_rule.amount = amount
            logging.info(f'Выбран объем - {self._task_rule.amount}')
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
            self._task_rule.fee = amount
            logging.info(f'Введена комиссия - {self._task_rule.fee}')
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
        self._task_rule.comment = message_str
        logging.info(f'Выбран комментарий - "{self._task_rule.comment}"')
        self._input_create_task()

    def _input_create_task(self):
        """
        Создание задания на создание счета юзера
        """
        logging.info(f'Создание задания на создание счета юзера')
        self._task_rule.run()
        self._connect_telebot.send_text('Команда выполнена.')
