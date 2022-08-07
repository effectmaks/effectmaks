import logging

from base.cash import ModelCash
from base.coin import ModelCoin
from telegram_bot.api.commandsWork import CommandsWork
from telegram_bot.api.telegramApi import ConnectTelebot

from .nextfunction import NextFunction
from business_model.taskrule import TaskRule
from business_model.simpledate import SimpleDate
from business_model.choicesafe import ChoiceSafe, ChoiceSafeResult


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
        self._next_function = NextFunction(OperationBank.__name__)
        self._simple_date: SimpleDate = None
        self._choice_safe: ChoiceSafe = None
        self._dict_safes_user = {}
        self._coin_list = []
        self._task_rule: TaskRule
        self._MODE_ADD = 'ДОБАВИТЬ'

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
            self._check_simple_date()  # далее выполнить

    def _check_simple_date(self):
        """
        Команда проверить наличие даты и времени
        """
        if self._simple_date.result:
            logging.info('Выбрана дата и время')
            self._work_choice_safe()
        else:
            raise ExceptionOperationBank('SimpleDate завершил свою работу, но даты в результате нет.')

    def _work_choice_safe(self):
        """
        Команда сформировать id_safe_user
        """
        if not self._choice_safe:
            self._choice_safe = ChoiceSafe(self._connect_telebot)
        working: bool = self._choice_safe.work()
        if working:
            self._next_function.set(self._work_choice_safe)
        else:
            self._input_coin_question()  # далее выполнить

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
