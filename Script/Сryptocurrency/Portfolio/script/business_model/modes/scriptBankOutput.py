import logging

from business_model.choice.choicecash import ChoiceCash, ModesChoiceCash
from business_model.choice.folderChoiceFloat.choicefloat import ChoiceFloat
from business_model.choice.choicetext import ChoiceText
from business_model.helpers.nextfunction import NextFunction
from telegram_bot.api.commandsWork import CommandsWork
from telegram_bot.api.telegramApi import ConnectTelebot
from business_model.taskrule import TaskRule
from business_model.choice.choicedate import ChoiceDate
from business_model.choice.choicesafe import ChoiceSafe, ModesChoiceSafe


class ExceptionScriptBankOutput(Exception):
    def __init__(self, err_message: str = ''):
        logging.error(f'Класс {ExceptionScriptBankOutput.__name__} - {err_message}')
        super().__init__(err_message)


class ScriptBankOutput:
    """
    Операции ввода, вывода и конвертации средств
    """
    def __init__(self, connect_telebot: ConnectTelebot):
        logging.info('Создание объекта ScriptBankOutput')
        self._connect_telebot = connect_telebot
        self._next_function = NextFunction(ScriptBankOutput.__name__)
        self._next_function.set(self._work_choice_date)
        self._check_date_time: ChoiceDate = None
        self._choice_safe: ChoiceSafe = None
        self._choice_cash: ChoiceCash = None
        self._choice_amount_first: ChoiceFloat = None
        self._choice_amount_second: ChoiceFloat = None
        self._fee: float
        self._choice_comment: ChoiceText = None

    def work(self):
        """
        Работа класса, в зависимости от команды, опрашивает пользователя
        """
        if self._next_function.work():  # функция выполнилась
            return

    def _work_choice_date(self):
        """
        Команда сформировать дату и время
        """
        if not self._check_date_time:
            self._check_date_time = ChoiceDate(self._connect_telebot)
        working: bool = self._check_date_time.work()
        if working:
            self._next_function.set(self._work_choice_date)
        else:
            logging.info('Выбран date_time')
            self._work_choice_safe()

    def _work_choice_safe(self):
        """
        Команда сформировать id_safe_user
        """
        if not self._choice_safe:
            self._choice_safe = ChoiceSafe(self._connect_telebot, ModesChoiceSafe.VIEW, 'Выберите тип сейфа:')
        working: bool = self._choice_safe.work()
        if working:
            self._next_function.set(self._work_choice_safe)  # еще не выбрано, повторить
        else:
            logging.info('Выбран id_safe_user')
            self._work_choice_cash()  # далее выполнить

    def _work_choice_cash(self):
        """
        Команда сформировать id_safe_user
        """
        if not self._choice_cash:
            self._choice_cash = ChoiceCash(self._connect_telebot, self._choice_safe.result.id_safe,
                                           message='Выберите счет вывода:')
        working: bool = self._choice_cash.work()
        if working:
            self._next_function.set(self._work_choice_cash)  # еще не выбрано, повторить
        else:
            logging.info('Выбран id_cash')
            self._work_choice_amount_first()  # далее выполнить

    def _work_choice_amount_first(self):
        """
        Команда сформировать amount
        """
        if not self._choice_amount_first:
            self._choice_amount_first = ChoiceFloat(self._connect_telebot,
                                                    question_main='Введите сколько было выведено:',
                                                    max_number=self._choice_cash.result_first_item.amount)
        working: bool = self._choice_amount_first.work()
        if working:
            self._next_function.set(self._work_choice_amount_first)  # еще не выбрано, повторить
        else:
            logging.info('Выбран _choice_amount_sell')
            self._work_choice_amount_second()  # далее выполнить

    def _work_choice_amount_second(self):
        """
        Команда сформировать fee
        """
        if not self._choice_amount_second:
            self._choice_amount_second = ChoiceFloat(self._connect_telebot,
                                                     question_main='Введите какой объем получен:',
                                                     max_number=self._choice_cash.result_first_item.amount)
        working: bool = self._choice_amount_second.work()
        if working:
            self._next_function.set(self._work_choice_amount_second)  # еще не выбрано, повторить
        else:
            logging.info('Выбран _choice_amount_buy')
            self._calc_fee()  # далее выполнить

    def _calc_fee(self):
        """
        Вычисление комиссии
        """
        logging.info('Вычисление комиссии')
        self._fee = self._choice_amount_first.result - self._choice_amount_second.result
        self._connect_telebot.send_text(f'Комиссия составила: {self._fee}')
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
        task_rule = TaskRule(self._connect_telebot.id_user, CommandsWork.COMMAND_OUTPUT)
        task_rule.date_time = self._check_date_time.result
        task_rule.id_cash = self._choice_cash.result_first_item.id_cash
        task_rule.id_safe_user = self._choice_safe.result.id_safe
        task_rule.amount = self._choice_amount_first.result
        task_rule.fee = self._fee
        task_rule.comment = self._choice_comment.result
        task_rule.run()
        self._connect_telebot.send_text('Команда выполнена.')
