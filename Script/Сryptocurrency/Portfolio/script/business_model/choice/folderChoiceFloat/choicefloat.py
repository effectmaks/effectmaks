import logging
from decimal import Decimal

from business_model.choice.folderChoiceFloat.questionAmount import QuestionAmount, TypesAnswerAmount
from business_model.helpers.nextfunction import NextFunction
from business_model.helpers.questionYesNo import QuestionYesNo
from telegram_bot.api.telegramApi import ConnectTelebot


class ExceptionChoiceFloat(Exception):
    def __init__(self, err_message: str = ''):
        logging.error(f'Класс {ExceptionChoiceFloat.__name__} - {err_message}')
        super().__init__(err_message)


class ChoiceFloat:
    def __init__(self, connect_telebot: ConnectTelebot, question_main: str, max_number: Decimal = 0):
        self._connect_telebot = connect_telebot
        self._question_main = question_main
        self._max_number = max_number
        self._next_function = NextFunction(ChoiceFloat.__name__)
        self._next_function.set(self._input_float_question)  # первое что выполнит скрипт
        self._question_amount: QuestionAmount
        self._result_float: Decimal = None
        self._zero = False
        self._question_yes_no: QuestionYesNo
        self._work = True
        self._choice_type_amount: TypesAnswerAmount  = None

    def _input_float_question(self):
        """
        Режим вопроса
        """
        logging.info(f'Режим вопроса - {self._question_main}')
        self._connect_telebot.send_text(self._question_main)
        self._next_function.set(self._input_float_answer)

    def _input_float_answer(self):
        """
        Режим проверка ответа
        :return:
        """
        logging.info(f'Режим проверки ответа на - {self._question_main}')
        message: str = self._connect_telebot.message
        result_float = self._isfloat(message)
        if message == '0':
            self._zero = True
        if result_float or self._zero:
            if self._check_min_max(result_float):
                self._work_end(result_float)
            else:
                self._set_question_amount()
        else:
            logging.info('Невозможно преобразовать число.')
            self._err__float_answer("Ошибка преобразования числа.")

    def _work_end(self, result_float: Decimal):
        self._result_float = result_float
        logging.info(f'Выбрано число - {self._result_float}')
        self._work = False

    def _set_question_amount(self):
        logging.info(f'Число должно быть от 0 до {self._max_number}.')
        self._question_amount = QuestionAmount(self._connect_telebot,
                                               text_err='Введенный объем превышает объем счета.')
        self._wait_question_amount()

    def _wait_question_amount(self):
        b_working = self._question_amount.work()
        if b_working:
            self._next_function.set(self._wait_question_amount)
            return
        result = self._question_amount.result
        if result == TypesAnswerAmount.REPEAT_AMOUNT:
            self._input_float_question()  # повторить ввод объема
        elif result == TypesAnswerAmount.CHOICE_CASH:
            self._choice_type_amount = result
            self._input_float_question()  # какой объем будет снят
        elif result == TypesAnswerAmount.CANCEL:
            raise ExceptionChoiceFloat(f'Пользователь решил остановить работу режима')
        else:
            raise ExceptionChoiceFloat(f'Пользователь не выбрал пункт из списка AMOUNT')

    def _err__float_answer(self, message_err: str):

        self._question_yes_no = QuestionYesNo(self._connect_telebot, message_err)
        self._wait_answer_repeat()

    def _check_min_max(self, result: Decimal) -> bool:
        if not self._max_number:
            return True
        elif result > self._max_number and self._choice_type_amount == TypesAnswerAmount.CHOICE_CASH:
            return True
        elif 0 <= result <= self._max_number:
            return True
        elif result <= self._max_number and self._choice_type_amount == TypesAnswerAmount.CHOICE_CASH:
            self._connect_telebot.send_text(f'Число должно быть больше {self._max_number}')

    def _wait_answer_repeat(self):
        b_working = self._question_yes_no.work()
        if b_working:
            self._next_function.set(self._wait_answer_repeat)
            return
        result: bool = self._question_yes_no.result
        if result:
            self._input_float_question()  # повторить
        else:
            raise ExceptionChoiceFloat(f'Невозможно преобразовать число - {self._connect_telebot.message}')

    def _isfloat(self, value_str: str) -> Decimal:
        try:
            value_str = value_str.replace(',', '.')
            return Decimal(value_str)
        except ValueError:
            pass

    @property
    def result(self) -> Decimal:
        return self._result_float

    @property
    def choice_type_amount(self) -> TypesAnswerAmount:
        return self._choice_type_amount

    def work(self) -> bool:
        self._next_function.work()
        if self._zero:
            return False
        return self._work
