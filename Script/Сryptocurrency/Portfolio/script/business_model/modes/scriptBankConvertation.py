import logging

from business_model.choice.choicecash import ChoiceCash
from business_model.choice.choicecoin import ChoiceCoin
from business_model.choice.choicedate import ChoiceDate
from business_model.choice.choicefloat import ChoiceFloat
from business_model.choice.choicesafe import ChoiceSafe, ModesChoiceSafe
from business_model.choice.choicetext import ChoiceText
from business_model.nextfunction import NextFunction
from business_model.questionYesNo import QuestionYesNo
from business_model.taskrule import TaskRule
from telegram_bot.api.commandsWork import CommandsWork
from telegram_bot.api.telegramApi import ConnectTelebot


class ExceptionScriptBankConvertation(Exception):
    def __init__(self, err_message: str = ''):
        logging.error(f'Класс {ExceptionScriptBankConvertation.__name__} - {err_message}')
        super().__init__(err_message)


class ScriptBankConvertation:
    """
        Операция конвертации средств
    """

    def __init__(self, connect_telebot: ConnectTelebot):
        logging.info('Создание объекта OperationBank')
        self._connect_telebot = connect_telebot
        self._next_function = NextFunction(ScriptBankConvertation.__name__)
        self._next_function.set(self._work_choice_date)
        self._question_yes_no: QuestionYesNo
        self._check_date_time: ChoiceDate = None
        self._choice_safe: ChoiceSafe = None
        self._choice_coin_buy: ChoiceCoin = None
        self._choice_amount_buy_before: ChoiceFloat = None
        self._choice_amount_buy_after: ChoiceFloat = None
        self._amount_buy: float
        self._choice_cash_sell: ChoiceCash = None
        self._choice_amount_sell_before: ChoiceFloat = None
        self._choice_amount_sell_after: ChoiceFloat = None
        self._amount_sell: float
        self._price_avr: float
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
            self._choice_safe = ChoiceSafe(self._connect_telebot, ModesChoiceSafe.VIEW)
        working: bool = self._choice_safe.work()
        if working:
            self._next_function.set(self._work_choice_safe)  # еще не выбрано, повторить
        else:
            logging.info('Выбран id_safe_user')
            self._work_choice_coin()  # далее выполнить

    def _work_choice_coin(self):
        """
        Команда сформировать coin buy
        """
        if not self._choice_coin_buy:
            self._choice_coin_buy = ChoiceCoin(self._connect_telebot, self._choice_safe.result.id_safe,
                                               'Выберите монету/валюту для покупки:')
        working: bool = self._choice_coin_buy.work()
        if working:
            self._next_function.set(self._work_choice_coin)
        else:
            logging.info('Выбран coin buy')
            self._work_choice_amount_buy_before()  # далее выполнить

    def _work_choice_amount_buy_before(self):
        """
        Команда сформировать amount buy before
        """
        if not self._choice_amount_buy_before:
            self._choice_amount_buy_before = ChoiceFloat(self._connect_telebot,
                                                         question_main=f'Введите сколько было '
                                                                       f'{self._choice_coin_buy.result} до покупки:')
        working: bool = self._choice_amount_buy_before.work()
        if working:
            self._next_function.set(self._work_choice_amount_buy_before)  # еще не выбрано, повторить
        else:
            logging.info('Выбран _work_choice_amount_buy_before')
            self._work_choice_amount_buy_after()  # далее выполнить

    def _work_choice_amount_buy_after(self):
        """
        Команда сформировать amount buy after
        """
        if not self._choice_amount_buy_after:
            self._choice_amount_buy_after = ChoiceFloat(self._connect_telebot,
                                                        question_main=f'Введите сколько получилось '
                                                                      f'{self._choice_coin_buy.result} после покупки:')
        working: bool = self._choice_amount_buy_after.work()
        if working:
            self._next_function.set(self._work_choice_amount_buy_after)  # еще не выбрано, повторить
        else:
            logging.info('Выбран _work_choice_amount_buy_after')
            self._calc_amount_buy()  # далее выполнить

    def _calc_amount_buy(self):
        """
        Вычисление amount_buy
        """
        logging.info('Вычисление amount_buy')
        self._amount_buy = self._choice_amount_buy_after.result - self._choice_amount_buy_before.result
        if self._amount_buy <= 0:
            self._question_yes_no = QuestionYesNo(self._connect_telebot, f"{self._amount_buy} "
                                                                         f"- не может быть отрицательным.")
            self._wait_calc_amount_buy_repeat()
            return
        self._connect_telebot.send_text(f'Куплен объем {self._choice_coin_buy.result}: {self._amount_buy}')
        self._work_choice_cash()  # далее выполнить

    def _wait_calc_amount_buy_repeat(self):
        b_working = self._question_yes_no.work()
        if b_working:
            self._next_function.set(self._wait_calc_amount_buy_repeat)
            return
        result: bool = self._question_yes_no.result
        if result:
            self._choice_amount_buy_before = None
            self._choice_amount_buy_after = None
            self._work_choice_amount_buy_before()  # повторить
        else:
            raise ExceptionScriptBankConvertation(f'Пользователь вводит неправильные числа.')

    def _work_choice_cash(self):
        """
        Команда сформировать id_cash
        """
        if not self._choice_cash_sell:
            self._choice_cash_sell = ChoiceCash(self._connect_telebot, self._choice_safe.result.id_safe,
                                                'Выберите счет продажи:')
        working: bool = self._choice_cash_sell.work()
        if working:
            self._next_function.set(self._work_choice_cash)  # еще не выбрано, повторить
        else:
            logging.info('Выбран id_cash')
            self._work_choice_amount_sell_before()  # далее выполнить

    def _work_choice_amount_sell_before(self):
        """
        Команда сформировать amount sell before
        """
        if not self._choice_amount_sell_before:
            max_number = self._choice_cash_sell.result.max_number
            self._choice_amount_sell_before = ChoiceFloat(self._connect_telebot,
                                                          question_main=f'Введите сколько было '
                                                                        f'{self._choice_cash_sell.result.coin} до '
                                                                        f'продажи:', max_number=max_number)
        working: bool = self._choice_amount_sell_before.work()
        if working:
            self._next_function.set(self._work_choice_amount_sell_before)  # еще не выбрано, повторить
        else:
            logging.info('Выбран _work_choice_amount_sell_before')
            self._work_choice_amount_sell_after()  # далее выполнить

    def _work_choice_amount_sell_after(self):
        """
        Команда сформировать amount sell after
        """
        if not self._choice_amount_sell_after:
            max_number = self._choice_cash_sell.result.max_number
            self._choice_amount_sell_after = ChoiceFloat(self._connect_telebot,
                                                         question_main=f'Введите объем '
                                                                       f'{self._choice_cash_sell.result.coin} после '
                                                                       f'продажи:', max_number=max_number)
        working: bool = self._choice_amount_sell_after.work()
        if working:
            self._next_function.set(self._work_choice_amount_sell_after)  # еще не выбрано, повторить
        else:
            logging.info('Выбран _work_choice_amount_sell_after')
            self._calc_amount_sell()  # далее выполнить

    def _calc_amount_sell(self):
        """
        Вычисление amount_sell
        """
        logging.info('Вычисление amount_sell')
        self._amount_sell = self._choice_amount_sell_before.result - self._choice_amount_sell_after.result
        if self._amount_sell <= 0:
            self._question_yes_no = QuestionYesNo(self._connect_telebot, f"{self._amount_sell} "
                                                                         f"- не может быть отрицательным.")
            self._wait_calc_amount_sell_repeat()
            return
        self._connect_telebot.send_text(f'Продан объем {self._choice_cash_sell.result.coin}: {self._amount_sell}')
        self._calc_price_avr()  # далее выполнить

    def _wait_calc_amount_sell_repeat(self):
        b_working = self._question_yes_no.work()
        if b_working:
            self._next_function.set(self._wait_calc_amount_sell_repeat)
            return
        result: bool = self._question_yes_no.result
        if result:
            self._choice_amount_sell_before = None
            self._choice_amount_sell_after = None
            self._work_choice_amount_sell_before()  # повторить
        else:
            raise ExceptionScriptBankConvertation(f'Пользователь вводит неправильные числа.')

    def _calc_price_avr(self):
        """
        Вычисление price_avr
        """
        logging.info('Вычисление price_avr')
        self._price_avr = self._amount_buy / self._amount_sell
        self._connect_telebot.send_text(f'Цена покупки {self._choice_coin_buy.result}/{self._choice_cash_sell.result.coin}: '
                                        f'{self._price_avr}')
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
        Создание задания на создание счетов продажи и покупки юзера
        """
        task_rule = TaskRule(self._connect_telebot.id_user, CommandsWork.COMMAND_CONVERTATION)
        task_rule.date_time = self._check_date_time.result
        task_rule.coin = self._choice_coin_buy
        task_rule.amount = self._amount_buy

        task_rule.id_cash_ = self._choice_cash_sell.result.id_cash  # Откуда снимать
        task_rule.amount_sell = self._amount_sell
        task_rule.id_safe_user = self._choice_safe.result.id_safe

        task_rule.comment = self._choice_comment.result
        task_rule.run()
        self._connect_telebot.send_text('Команда выполнена.')
