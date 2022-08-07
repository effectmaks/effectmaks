from telegram_bot.api.telegramApi import ConnectTelebot
from business_model.nextfunction import NextFunction


class QuestionYesNo:
    def __init__(self, connect_telebot: ConnectTelebot):
        self._connect_telebot = connect_telebot
        self._next_function = NextFunction(QuestionYesNo.__name__)
        self._next_function.set(self._set_question)
        self._YES = 'ДА'
        self._NO = 'НЕТ'
        self._list_options = [self._YES, self._NO]
        self._choice: bool = False
        self._result: bool = False

    def _set_question(self):
        """
        Сформировать вопрос
        """
        self._connect_telebot.view_keyboard_yes_no('Ошибка преобразования даты.\n Желаете повторить?',
                                                   self._YES, self._NO)
        self._next_function.set(self._answer)

    def _answer(self):
        if self._connect_telebot.message in self._list_options:
            if self._connect_telebot.message == self._YES:
                self._choice = True
            self._result = True
        else:
            self._set_question()

    @property
    def result(self):
        return self._choice

    def work(self) -> bool:
        self._next_function.work()
        if not self._result:
            return True