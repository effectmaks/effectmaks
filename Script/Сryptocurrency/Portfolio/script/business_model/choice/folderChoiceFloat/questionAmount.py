import logging
from enum import Enum

from telegram_bot.api.telegramApi import ConnectTelebot, MessageType
from business_model.helpers.nextfunction import NextFunction


class ExceptionQuestionAmount(Exception):
    def __init__(self, err_message: str = ''):
        logging.error(f'Класс {QuestionAmount.__name__} - {err_message}')
        super().__init__(err_message)


class TypesAnswerAmount(Enum):
    REPEAT_AMOUNT = 'Изменить объем'
    CHOICE_CASH = 'Выбрать счет'
    CANCEL = 'Отменить'


class QuestionAmount:
    def __init__(self, connect_telebot: ConnectTelebot, text_err: str):
        self._connect_telebot = connect_telebot
        self._next_function = NextFunction(QuestionAmount.__name__)
        self._next_function.set(self._set_question)

        self._dict_options = {TypesAnswerAmount.REPEAT_AMOUNT.name: 'ВВЕСТИ ОБЪЕМ',
                              TypesAnswerAmount.CHOICE_CASH.name: 'ДОБАВИТЬ СЧЕТ',
                              TypesAnswerAmount.CANCEL.name: 'ОТМЕНИТЬ'}
        self._choice: TypesAnswerAmount = None
        self._result: bool = False
        self._text_err: str = text_err

    def _set_question(self):
        """
        Сформировать вопрос Что делать с объемом?
        """
        logging.info('Режим вопрос Что делать с объемом?')
        self._connect_telebot.view_keyboard(f'{self._text_err}\nВыберите действие:',
                                            dict_view=self._dict_options,
                                            type_message=MessageType.KEY)
        self._next_function.set(self._answer)

    def _answer(self):
        if self._connect_telebot.message in self._dict_options.keys():
            if self._connect_telebot.message == TypesAnswerAmount.REPEAT_AMOUNT.name:
                self._choice = TypesAnswerAmount.REPEAT_AMOUNT
            elif self._connect_telebot.message == TypesAnswerAmount.CHOICE_CASH.name:
                self._choice = TypesAnswerAmount.CHOICE_CASH
            elif self._connect_telebot.message == TypesAnswerAmount.CANCEL.name:
                raise ExceptionQuestionAmount('Юзер отказался от дальнейших действий с объемом.')
            self._result = True
        else:
            self._set_question()

    @property
    def result(self) -> TypesAnswerAmount:
        return self._choice

    def work(self) -> bool:
        self._next_function.work()
        if not self._result:
            return True