import logging

from business_model.nextfunction import NextFunction
from business_model.questionYesNo import QuestionYesNo
from telegram_bot.api.telegramApi import ConnectTelebot


class ExceptionChoiceFloat(Exception):
    def __init__(self, err_message: str = ''):
        logging.error(f'Класс {ExceptionChoiceFloat.__name__} - err_message')
        super().__init__(err_message)


class ChoiceFloat:
    def __init__(self, connect_telebot: ConnectTelebot, question_main: str, ):
        self._connect_telebot = connect_telebot
        self._question_main = question_main
        self._next_function = NextFunction(ChoiceFloat.__name__)
        self._next_function.set(self._input_float_question)  # первое что выполнит скрипт
        self._result_float: float = 0
        self._question_yes_no: QuestionYesNo

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
        result_float = self._isfloat(self._connect_telebot.message)
        if result_float:
            self._result_float = result_float
            logging.info(f'Выбрано число - {self._result_float}')
        else:
            logging.info('Невозможно преобразовать число.')
            self._question_yes_no = QuestionYesNo(self._connect_telebot, "Ошибка преобразования числа.")
            self._wait_answer_repeat()

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

    def _isfloat(self, value_str: str) -> float:
        try:
            value_str = value_str.replace(',', '.')
            return float(value_str)
        except ValueError:
            pass

    @property
    def result(self) -> float:
        return self._result_float

    def work(self) -> bool:
        self._next_function.work()
        if not self._result_float:
            return True