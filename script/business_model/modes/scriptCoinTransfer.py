import logging

from business_model.choice.choicecash import ChoiceCash, ModesChoiceCash
from business_model.choice.choicecoin import ChoiceCoin, ModesChoiceCoin
from business_model.choice.folderChoiceFloat.choicefloat import ChoiceFloat, TypesChoiceFloat
from business_model.choice.choicetext import ChoiceText
from business_model.choice.folderChoiceFloat.questionAmount import TypesAnswerAmount
from business_model.helpers.nextfunction import NextFunction
from telegram_bot.api.commandsWork import CommandsWork, TypeWork
from telegram_bot.api.telegramApi import ConnectTelebot
from business_model.taskrule import TaskRule
from business_model.choice.choicedate import ChoiceDate
from business_model.choice.choicesafe import ChoiceSafe, ModesChoiceSafe


class ExceptionScriptCoinTransfer(Exception):
    def __init__(self, err_message: str = ''):
        logging.error(f'Класс {ExceptionScriptCoinTransfer.__name__} - {err_message}')
        super().__init__(err_message)


class ScriptCoinTransfer:
    """
    Операции ввода, вывода и конвертации средств
    """
    def __init__(self, connect_telebot: ConnectTelebot):
        logging.info('Создание объекта ScriptCoinTransfer')
        self._connect_telebot = connect_telebot
        self._next_function = NextFunction(ScriptCoinTransfer.__name__)
        self._next_function.set(self._work_choice_date)
        self._check_date_time: ChoiceDate = None
        self._choice_coin_sell: ChoiceCoin = None
        self._choice_safe_sell: ChoiceSafe = None
        self._choice_cash_sell: ChoiceCash = None

        self._choice_safe_buy: ChoiceSafe = None
        self._choice_cash_buy: ChoiceCash = None

        self._choice_amount_sell: ChoiceFloat = None
        self._choice_amount_buy: ChoiceFloat = None
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
            logging.info('Выбран date_time_str')
            self._work_choice_safe_sell()

    def _work_choice_safe_sell(self):
        """
        Команда сформировать id_safe_sell
        """
        if not self._choice_safe_sell:
            self._choice_safe_sell = ChoiceSafe(self._connect_telebot, ModesChoiceSafe.VIEW,
                                                'Выберите тип сейфа снятия:')
        working: bool = self._choice_safe_sell.work()
        if working:
            self._next_function.set(self._work_choice_safe_sell)  # еще не выбрано, повторить
        else:
            logging.info('Выбран id_safe_sell')
            self._work_choice_coin_sell()  # далее выполнить

    def _work_choice_coin_sell(self):
        """
        Команда сформировать coin sell
        """
        if not self._choice_coin_sell:
            self._choice_coin_sell = ChoiceCoin(self._connect_telebot, self._choice_safe_sell.result.id_safe,
                                               'Выберите монету/валюту для перевода:', ModesChoiceCoin.VIEW)
        working: bool = self._choice_coin_sell.work()
        if working:
            self._next_function.set(self._work_choice_coin_sell)
        else:
            logging.info('Выбран coin sell')
            self._work_choice_cash_sell()  # далее выполнить

    def _work_choice_cash_sell(self):
        """
        Команда сформировать id_cash_sell снятия
        """
        if not self._choice_cash_sell:
            self._choice_cash_sell = ChoiceCash(self._connect_telebot, self._choice_safe_sell.result.id_safe,
                                                message='Выберите счет снятия:',
                                                filter_coin_view=self._choice_coin_sell.result,
                                                filter_cash_date_before=self._check_date_time.result)
        working: bool = self._choice_cash_sell.work()
        if working:
            self._next_function.set(self._work_choice_cash_sell)  # еще не выбрано, повторить
        else:
            logging.info('Выбран список id_cash_sell')
            self._work_choice_safe_buy()  # далее выполнить

    def _work_choice_safe_buy(self):
        """
        Команда сформировать id_safe_buy
        """
        if not self._choice_safe_buy:
            self._choice_safe_buy = ChoiceSafe(self._connect_telebot,
                                               ModesChoiceSafe.CREATE,
                                               message='Выберите тип сейфа пополнения:',
                                               view_no_safe_id=self._choice_safe_sell.result.id_safe)
        working: bool = self._choice_safe_buy.work()
        if working:
            self._next_function.set(self._work_choice_safe_buy)  # еще не выбрано, повторить
        else:
            logging.info('Выбран id_safe_buy')
            self._work_choice_amount_first()  # далее выполнить

    def _work_choice_amount_first(self):
        """
        Команда сформировать _choice_amount_sell
        """
        if not self._choice_amount_sell:
            self._choice_amount_sell = ChoiceFloat(self._connect_telebot,
                                                   question_main=f'Введите сколько было выведено '
                                                                 f'{self._choice_cash_sell.result_first_item.coin}:',
                                                   max_number=self._choice_cash_sell.result_first_item.amount,
                                                   type_work=TypesChoiceFloat.CASH)
        working: bool = self._choice_amount_sell.work()
        if working:
            self._next_function.set(self._work_choice_amount_first)  # еще не выбрано, повторить
        else:
            self._check_work_choice_amount_first()

    def _check_work_choice_amount_first(self):
        """
        Проверить выбрано число или нужно выбирать дополнительные счета
        :return:
        """
        if self._choice_amount_sell.choice_type_amount == TypesAnswerAmount.CHOICE_CASH:
            logging.info('Нужно выбрать дополнительные счета')
            self._choice_cash_sell.set_type_amount_list(self._choice_amount_sell.result)
            self._work_choice_cash_sell_list()  # выбрать дополнительные счета
            self._next_function.set(self._work_choice_cash_sell_list)
        else:
            logging.info('Дополнительные счета вводить не требуется')
            # установить сколько надо перевести средств со счета
            self._choice_cash_sell.result_first_item.amount = self._choice_amount_sell.result
            self._work_choice_amount_second()  # далее выполнить

    def _work_choice_cash_sell_list(self):
        """
        Выбрать дополнительные счета для продажи в режиме CHOICE_CASH
        """
        logging.info('Работа _choice_cash_sell в режиме CHOICE_CASH')
        working: bool = self._choice_cash_sell.work()
        if working:
            self._next_function.set(self._work_choice_cash_sell)  # еще не выбрано, повторить
        else:
            logging.info('Выбран id_cash_sell в режиме CHOICE_CASH')
            self._choice_cash_sell.amount_sell = self._choice_amount_sell.result
            self._work_choice_amount_second()  # далее выполнить

    def _work_choice_amount_second(self):
        """
        Команда сформировать _choice_amount_buy
        """
        if not self._choice_amount_buy:
            self._choice_amount_buy = ChoiceFloat(self._connect_telebot,
                                                  question_main='Введите какой объем получен:',
                                                  max_number=self._choice_cash_sell.amount_sell)
        working: bool = self._choice_amount_buy.work()
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
        self._fee = self._choice_amount_sell.result - self._choice_amount_buy.result
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
        task_rule = TaskRule(self._connect_telebot.id_user, TypeWork.TYPE_COIN_TRANSFER)
        task_rule.date_time = self._check_date_time.result
        task_rule.id_safe_user = self._choice_safe_buy.result.id_safe  # перевести
        task_rule.safe_buy_name = self._choice_safe_buy.result.safe_name
        task_rule.safe_sell_name = self._choice_safe_sell.result.safe_name
        task_rule.list_cash = self._choice_cash_sell.list_result

        task_rule.amount_sell = self._choice_amount_sell.result
        task_rule.amount = self._choice_amount_buy.result
        task_rule.fee = self._fee
        task_rule.comment = self._choice_comment.result
        task_rule.run()
        self._connect_telebot.send_text('Команда выполнена.')
