import logging

from base.cash import ModelCash
from base.coin import ModelCoin
from base.safelist import Safetypes, ModelSafelist
from base.safeuser import ModelSafeuser
from telegram_bot.api.commandsWork import CommandsWork
from telegram_bot.api.telegramApi import ConnectTelebot

from .nextfunction import NextFunction
from business_model.taskrule import TaskRule
from business_model.simpledate import SimpleDate


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
        self._simple_date: SimpleDate = None
        self._command_now = command_now
        self._connect_telebot = connect_telebot
        self._next_function = NextFunction(OperationBank.__name__)
        self._MODE_ADD = 'ДОБАВИТЬ'
        self._dict_safes_user = {}
        self._coin_list = []
        self._task_rule: TaskRule

    def work(self):
        """
        Работа класса, в зависимости от команды, опрашивает пользователя
        """
        if self._next_function.work():  # функция выполнилась
            return
        if self._command_now == CommandsWork.COMMAND_INPUT:
            self._task_rule = TaskRule(id_user=self._connect_telebot.id_user, command_type=CommandsWork.COMMAND_INPUT)
            self._work_simple_date()

    def _work_simple_date(self):
        """
        Команда сформировать дату и время
        """
        if not self._simple_date:
            self._simple_date = SimpleDate(self._connect_telebot)
        working: bool = self._simple_date.work()
        if working:
            self._next_function.set(self._work_simple_date)
        else:
            self._check_simple_date()

    def _check_simple_date(self):
        """
        Команда проверить наличие даты и времени
        """
        if self._simple_date.result:
            logging.info('Выбрана дата и время')
            self._input_safe_type()
        else:
            raise ExceptionOperationBank('SimpleDate завершил свою работу, но даты в результате нет.')

    def _input_safe_type(self):
        """
        Режим  формирование вопроса, на какой тип сейфа хотите пополнить.
        """
        logging.info(f'Режим задать вопрос, какой тип сейфа?')
        list_name: list = Safetypes.get_list()
        self._connect_telebot.view_keyboard('Выберите тип сейфа:', list_name=list_name)
        self._next_function.set(self._input_safe_type_check)

    def _input_safe_type_check(self):
        """
        Режим  проверяет ответ пользователя, по типу сейфа.
        Если правильно выбран, запоминает выбранный тип сейфа.
        """
        logging.info(f'Режим проверить "{self._connect_telebot.message}" - это тип?')
        if Safetypes.check(self._connect_telebot.message):
            self._task_rule.safe_type = self._connect_telebot.message
            self._input_safe_list()
        else:
            self._connect_telebot.send_text('Выбран неправильный тип сейфа.')
            raise ExceptionOperationBank(f'Выбран не правильный тип сейфа - {self._connect_telebot.message}')

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

    def _input_safe_list_check(self):
        """
        Проверка какой сейф выбрали с типом self._task_rule.safe_type.
        Или переход на шаг создания нового сейфа с типом self._task_rule.safe_type.
        """
        if self._connect_telebot.message == self._MODE_ADD:
            self._create_safe_question()
        else:
            id_safe = self._dict_safes_user.get(self._connect_telebot.message)
            if id_safe:
                self._task_rule.safe_name = self._connect_telebot.message
                self._task_rule.id_safe_user = id_safe
                logging.info(f'Выбран сейф ID_safe_user:{self._task_rule.id_safe_user} name:"{self._task_rule.safe_name}"')
                self._input_coin_question()
            else:
                self._connect_telebot.send_text(f'Такого сейфа "{self._connect_telebot.message}" нет в списке.')
                raise ExceptionOperationBank(f'Пользователь выбрал сейф - "{self._connect_telebot.message}", он не из списка.')

    def _create_safe_question(self):
        """
        Вопрос - какое имя сейфа создавать?
        """
        logging.info(f'Режим создания сейфа с типом "{self._task_rule.safe_type}"')
        self._connect_telebot.send_text(f'Введите название сейфа с типом - "{self._task_rule.safe_type}":')
        self._next_function.set(self._create_safe_answer)

    def _create_safe_answer(self):
        """
        Создать новый сейф у юзера
        """
        logging.info(f'Режим проверки названия сейфа "{self._connect_telebot.message}"')
        message_str = self._connect_telebot.message.upper()
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

    def _input_coin_answer(self):
        """
        Проверить,монета из списка?
        Иначе добавить.
        """
        logging.info(f'Режим проверка монеты из списка.')
        if self._connect_telebot.message == self._MODE_ADD:
            self._create_coin_question()
        else:
            if self._connect_telebot.message in self._coin_list:
                self._task_rule.coin = self._connect_telebot.message
                logging.info(f'Выбрана монета "{self._task_rule.coin}"')
                self._input_amount_question()
            else:
                self._connect_telebot.send_text(f'Пункта "{self._connect_telebot.message}" нет в списке.')
                raise ExceptionOperationBank(f'Пользователь выбрал пункт - "{self._connect_telebot.message}", он не из списка.')

    def _create_coin_question(self):
        """
        Режим вопрос - какое имя монеты создавать?
        """
        logging.info(f'Режим создания монеты.')
        coin_list = ModelCoin.get_list()
        self._connect_telebot.view_keyboard('Напишите или выберите монету/валюту:', list_name=coin_list)
        self._next_function.set(self._create_coin_answer)

    def _create_coin_answer(self):
        """
        Создать новую монету
        """
        logging.info(f'Режим проверки названия монеты "{self._connect_telebot.message}"')
        message_str = self._connect_telebot.message.upper()
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

    def _input_amount_answer(self):
        """
        Режим проверка объема пополнения пользователя
        :return:
        """
        logging.info(f'Режим проверки объема пополнения')
        amount = self._isfloat(self._connect_telebot.message)
        if amount:
            self._task_rule.amount = amount
            logging.info(f'Выбран объем - {self._task_rule.amount}')
            self._input_fee_question()
        else:
            self._connect_telebot.send_text('Невозможно преобразовать число.')
            raise ExceptionOperationBank(f'Невозможно преобразовать число - {self._connect_telebot.message}')

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

    def _input_fee_answer(self):
        """
        Режим проверка комиссия пользователя
        :return:
        """
        logging.info(f'Режим проверки комиссии')
        amount = self._isfloat(self._connect_telebot.message)
        if amount:
            self._task_rule.fee = amount
            logging.info(f'Введена комиссия - {self._task_rule.fee}')
            self._input_comment_question()
        else:
            self._connect_telebot.send_text('Невозможно преобразовать число.')
            raise ExceptionOperationBank(f'Невозможно преобразовать число - {self._connect_telebot.message}')

    def _input_comment_question(self):
        """
        Режим вопроса, введите комментарий
        """
        logging.info(f'Режим ввода комментария')
        self._connect_telebot.send_text(f'Введите комментарий:')
        self._next_function.set(self._input_comment_answer)

    def _input_comment_answer(self):
        """
        Проверка комментария
        :return:
        """
        logging.info(f'Режим проверки комментария')
        self._task_rule.comment = self._connect_telebot.message
        logging.info(f'Выбран комментарий - "{self._task_rule.comment}"')
        self._input_create_task()

    def _input_create_task(self):
        """
        Создание задания на создание счета юзера
        """
        self._task_rule.run()
        self._connect_telebot.send_text('Команда выполнена.')
