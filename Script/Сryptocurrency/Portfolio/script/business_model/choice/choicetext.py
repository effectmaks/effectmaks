import logging

from business_model.nextfunction import NextFunction
from telegram_bot.api.telegramApi import ConnectTelebot


class ExceptionChoiceText(Exception):
    def __init__(self, err_message: str = ''):
        logging.error(f'Класс {ExceptionChoiceText.__name__} - {err_message}')
        super().__init__(err_message)


class ChoiceText:
    def __init__(self, connect_telebot: ConnectTelebot, question_main: str, ):
        self._connect_telebot = connect_telebot
        self._question_main = question_main
        self._next_function = NextFunction(ChoiceText.__name__)
        self._next_function.set(self._input_text_question)  # первое что выполнит скрипт
        self._result_text: str = ""

    def _input_text_question(self):
        """
        Режим вопроса
        """
        logging.info(f'Режим вопроса - {self._question_main}')
        self._connect_telebot.send_text(self._question_main)
        self._next_function.set(self._input_text_answer)

    def _input_text_answer(self):
        """
        Режим проверка ответа
        :return:
        """
        logging.info(f'Режим проверки ответа на - {self._question_main}')
        self._result_text = self._connect_telebot.message

    @property
    def result(self) -> str:
        return self._result_text

    def work(self) -> bool:
        self._next_function.work()
        if not self._result_text:
            return True