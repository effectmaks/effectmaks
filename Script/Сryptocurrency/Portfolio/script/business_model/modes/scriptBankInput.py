import logging

from business_model.choice.choicecoin import ChoiceCoin
from business_model.choice.choicefloat import ChoiceFloat
from business_model.choice.choicetext import ChoiceText
from business_model.nextfunction import NextFunction
from telegram_bot.api.commandsWork import CommandsWork
from telegram_bot.api.telegramApi import ConnectTelebot
from business_model.taskrule import TaskRule
from business_model.choice.choicedate import ChoiceDate
from business_model.choice.choicesafe import ChoiceSafe


class ExceptionScriptBankInput(Exception):
    def __init__(self, err_message: str = ''):
        logging.error(f'Класс {ExceptionScriptBankInput.__name__} - {err_message}')
        super().__init__(err_message)


class ScriptBankInput:
    """
    Операции ввода, вывода и конвертации средств
    """
    def __init__(self, connect_telebot: ConnectTelebot):
        logging.info('Создание объекта OperationBank')
        self._connect_telebot = connect_telebot
        self._next_function = NextFunction(ScriptBankInput.__name__)
        self._next_function.set(self._work_simple_date)
        self._check_date_time: ChoiceDate = None
        self._choice_safe: ChoiceSafe = None
        self._choice_coin: ChoiceCoin = None
        self._choice_amount: ChoiceFloat = None
        self._choice_fee: ChoiceFloat = None
        self._choice_comment: ChoiceText = None

    def work(self):
        """
        Работа класса, в зависимости от команды, опрашивает пользователя
        """
        if self._next_function.work():  # функция выполнилась
            return

    def _work_simple_date(self):
        """
        Команда сформировать дату и время
        """
        if not self._check_date_time:
            self._check_date_time = ChoiceDate(self._connect_telebot)
        working: bool = self._check_date_time.work()
        if working:
            self._next_function.set(self._work_simple_date)
        else:
            logging.info('Выбран date_time')
            self._work_choice_safe()

    def _work_choice_safe(self):
        """
        Команда сформировать id_safe_user
        """
        if not self._choice_safe:
            self._choice_safe = ChoiceSafe(self._connect_telebot)
        working: bool = self._choice_safe.work()
        if working:
            self._next_function.set(self._work_choice_safe)  # еще не выбрано, повторить
        else:
            logging.info('Выбран id_safe_user')
            self._work_choice_coin()  # далее выполнить

    def _work_choice_coin(self):
        """
        Команда сформировать coin
        """
        if not self._choice_coin:
            self._choice_coin = ChoiceCoin(self._connect_telebot, self._choice_safe.result.id_safe)
        working: bool = self._choice_coin.work()
        if working:
            self._next_function.set(self._work_choice_coin)
        else:
            logging.info('Выбран coin')
            self._work_choice_float()  # далее выполнить

    def _work_choice_float(self):
        """
        Команда сформировать amount
        """
        if not self._choice_amount:
            self._choice_amount = ChoiceFloat(self._connect_telebot, question_main='Введите объем пополнения:')
        working: bool = self._choice_amount.work()
        if working:
            self._next_function.set(self._work_choice_float)  # еще не выбрано, повторить
        else:
            logging.info('Выбран amount')
            self._work_choice_fee()  # далее выполнить

    def _work_choice_fee(self):
        """
        Команда сформировать fee
        """
        if not self._choice_fee:
            self._choice_fee = ChoiceFloat(self._connect_telebot, question_main='Введите объем комиссии:')
        working: bool = self._choice_fee.work()
        if working:
            self._next_function.set(self._work_choice_fee)  # еще не выбрано, повторить
        else:
            logging.info('Выбран fee')
            self._work_choice_comment()  # далее выполнить

    def _work_choice_comment(self):
        """
        Команда сформировать comment
        """
        if not self._choice_comment:
            self._choice_comment = ChoiceText(self._connect_telebot, question_main='Введите комментарий:')
        working: bool = self._choice_comment.work()
        if working:
            self._next_function.set(self._work_choice_comment)  # еще не выбрано, повторить
        else:
            logging.info('Выбран comment')
            self._input_create_task()  # далее выполнить

    def _input_create_task(self):
        """
        Создание задания на создание счета юзера
        """
        task_rule = TaskRule(self._connect_telebot.id_user, CommandsWork.COMMAND_INPUT)
        task_rule.date_time = self._check_date_time.result
        task_rule.safe_type = self._choice_safe.result.safe_type
        task_rule.id_safe_user = self._choice_safe.result.id_safe
        task_rule.safe_name = self._choice_safe.result.safe_name
        task_rule.coin = self._choice_coin.result
        task_rule.amount = self._choice_amount.result
        task_rule.fee = self._choice_fee.result
        task_rule.comment = self._choice_comment.result
        task_rule.run()
        self._connect_telebot.send_text('Команда выполнена.')
