import logging
from typing import Dict

from base.models.cash import ModelCash, CashItem
from business_model.nextfunction import NextFunction
from business_model.questionYesNo import QuestionYesNo
from telegram_bot.api.telegramApi import ConnectTelebot


class ChoiceCashResult:
    def __init__(self):
        self.max_number: float = 0
        self.id_cash: int = 0
        self.coin: str = ""
        self.price_buy: float = 0
        self.coin_avr: str = ""

    def __bool__(self) -> bool:
        if self.id_cash != 0 and self.coin != "":
            return True
        return False


class ExceptionChoiceCash(Exception):
    def __init__(self, err_message: str = ''):
        logging.error(f'Класс {ExceptionChoiceCash.__name__} - {err_message}')
        super().__init__(err_message)


class ChoiceCash:
    def __init__(self, connect_telebot: ConnectTelebot, id_safe_user: int, message: str, filter_coin: str = ''):
        self._connect_telebot = connect_telebot
        self._next_function = NextFunction(ChoiceCash.__name__)
        self._next_function.set(self._question_choice_cash)  # первое что выполнит скрипт
        self._message_str: str = message
        self._dict_view: Dict
        self._dict_cash: Dict

        self._result = ChoiceCashResult()  # хранит результат выбора пользователя
        self._id_safe_user = id_safe_user
        self._filter_coin = filter_coin

    def _question_choice_cash(self):
        """
        Режим показать счета у сейфа
        """
        logging.info('Режим показать счета у сейфа')
        self._dict_cash: Dict[str, CashItem] = ModelCash.dict_amount(self._id_safe_user, self._filter_coin)
        if not self._dict_cash:
            self._connect_telebot.send_text('В сейфе нет счетов для продажи.')
            raise ExceptionChoiceCash('В сейфе нет счетов для продажи.')
        self._dict_view: Dict = {self._key_value(item): id for id, item in
                                 self._dict_cash.items()}
        self._connect_telebot.view_keyboard(self._message_str, dict_view=self._dict_view)
        self._next_function.set(self._answer_choice_cash)

    def _key_value(self, item: CashItem) -> str:
        price_avr: str = f'({item.coin_avr} {item.price_buy})'
        if price_avr == "(None 0.0)":
            price_avr = '(-)'
        return f'{item.coin}: {item.amount} {price_avr}'

    def _answer_choice_cash(self):
        """
        Проверка пользователя, какой счет он выбрал.
        """
        logging.info("Проверка пользователя, какой счет он выбрал.")
        try:
            choice_cash_info = self._connect_telebot.message
            id_cash = self._dict_view.get(choice_cash_info)
            if id_cash:
                logging.info(f'Выбран id_cash: {id_cash}')
                self._result.id_cash = id_cash
                self._result.max_number = self._dict_cash.get(id_cash).amount
                self._result.coin = self._dict_cash.get(id_cash).coin
                self._result.price_buy = self._dict_cash.get(id_cash).price_buy
                self._result.coin_avr = self._dict_cash.get(id_cash).coin_avr
            else:
                self._err_answer_choice_cash()
        except Exception as err:
            logging.info(f'Ошибка проверки счета. Сообщение - {self._connect_telebot.message}. ERR: {err}')
            self._err_answer_choice_cash()

    def _err_answer_choice_cash(self):
        self._question_yes_no = QuestionYesNo(self._connect_telebot,
                                              f'"{self._connect_telebot.message}" - счета нет в списке.')
        self._wait_answer_repeat_id_cash()

    def _wait_answer_repeat_id_cash(self):
        b_working = self._question_yes_no.work()
        if b_working:
            self._next_function.set(self._wait_answer_repeat_id_cash)
            return
        result: bool = self._question_yes_no.result
        if result:
            self._question_choice_cash()  # Повторить
        else:
            raise ExceptionChoiceCash('Юзер отказался выбирать счет.')

    @property
    def result(self) -> ChoiceCashResult:
        return self._result

    def work(self) -> bool:
        self._next_function.work()
        if not self._result:
            return True