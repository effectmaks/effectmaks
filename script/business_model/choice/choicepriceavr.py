import logging
from typing import Dict
from enum import Enum
from decimal import Decimal

from business_model.helpers.nextfunction import NextFunction
from business_model.helpers.questionYesNo import QuestionYesNo
from telegram_bot.api.telegramApi import ConnectTelebot


class ExceptionChoicePriceAvr(Exception):
    def __init__(self, err_message: str = ''):
        logging.error(f'Класс {ExceptionChoicePriceAvr.__name__} - {err_message}')
        super().__init__(err_message)


class TypeConvertatuion(Enum):
    BUY = 'BUY'
    SELL = 'SELL'
    NONE = 'NONE'


class ChoicePriceAvrResult:
    def __init__(self):
        self.type_convertation: TypeConvertatuion = TypeConvertatuion.NONE
        self.price_avr: Decimal = None

    def __bool__(self) -> bool:
        if self.price_avr != 0 and self.type_convertation != TypeConvertatuion.NONE:
            return True
        return False


class ChoicePriceAvr:
    def __init__(self, connect_telebot: ConnectTelebot, amount_sell: Decimal, amount_buy: Decimal):
        self._connect_telebot = connect_telebot
        self._amount_sell = amount_sell
        self._amount_buy = amount_buy
        self._next_function = NextFunction(ChoicePriceAvr.__name__)
        self._next_function.set(self._price_question)  # первое что выполнит скрипт
        self._result: ChoicePriceAvrResult = ChoicePriceAvrResult()
        self._question_yes_no: QuestionYesNo
        self._dict_variants: Dict[str, str]

    def _price_question(self):
        """
        Режим вопроса
        """
        logging.info(f'Режим вопроса - Выберите цену обмена:')

        self._dict_variants = {}
        number_1 = self._amount_sell / self._amount_buy
        number_1 = number_1.quantize(Decimal('0.000001'))
        price_avr_1 = str(number_1)
        self._dict_variants[price_avr_1] = TypeConvertatuion.BUY
        number_2 = self._amount_buy / self._amount_sell
        number_2 = number_2.quantize(Decimal('0.000001'))
        price_avr_2 = str(number_2)
        self._dict_variants[price_avr_2] = TypeConvertatuion.SELL
        self._connect_telebot.view_keyboard('Выберите цену обмена:', dict_view=self._dict_variants)
        self._next_function.set(self._price_answer)

    def _price_answer(self):
        """
        Юзер выбрал значение из списка
        """
        logging.info(f'Режим проверки ответа на - Выберите цену обмена:')
        message: str = self._connect_telebot.message
        if message in self._dict_variants:
            self._price_answer_check()
        else:
            logging.info('Юзер выбрал значение НЕ из списка.')
            self._question_yes_no = QuestionYesNo(self._connect_telebot, f"{message} - нет в списке.")
            self._wait_answer_repeat()

    def _wait_answer_repeat(self):
        b_working = self._question_yes_no.work()
        if b_working:
            self._next_function.set(self._wait_answer_repeat)
            return
        result: bool = self._question_yes_no.result
        if result:
            self._price_question()  # повторить да
        else:
            raise ExceptionChoicePriceAvr(f'Юзер отказался выбирать значение из списка.')

    def _price_answer_check(self):
        """
            Режим проверка ответа
        """
        message: str = self._connect_telebot.message
        self._result.type_convertation = self._dict_variants.get(message)
        self._result.price_avr = self._isfloat(message)

    def _isfloat(self, value_str: str) -> Decimal:
        try:
            value_str = value_str.replace(',', '.')
            return Decimal(value_str)
        except ValueError:
            pass

    @property
    def result(self) -> ChoicePriceAvrResult:
        return self._result

    def work(self) -> bool:
        self._next_function.work()
        if not self._result:
            return True