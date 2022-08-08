import logging

from base.safelist import Safetypes, ModelSafelist
from base.safeuser import ModelSafeuser
from business_model.nextfunction import NextFunction
from business_model.questionYesNo import QuestionYesNo
from telegram_bot.api.telegramApi import ConnectTelebot


class ExceptionChoiceSafe(Exception):
    def __init__(self, err_message: str = ''):
        logging.error(f'Класс {ExceptionChoiceSafe.__name__} - {err_message}')
        super().__init__(err_message)


class ChoiceSafeResult:
    def __init__(self):
        self.safe_type: str = ''
        self.safe_name: str = ''
        self.id_safe: int = 0

    def __bool__(self) -> bool:
        if self.safe_type != '' and self.safe_type != 0 and self.safe_name != '':
            return True
        return False


class ChoiceSafe:
    def __init__(self, connect_telebot: ConnectTelebot):
        self._connect_telebot = connect_telebot
        self._next_function = NextFunction(ChoiceSafe.__name__)
        self._next_function.set(self._input_safe_type)  # первое что выполнит скрипт
        self._result = ChoiceSafeResult() # класс хранит результат выбора пользователя
        self._MODE_ADD = 'ДОБАВИТЬ'

    def _input_safe_type(self):
        """
        Режим  формирование вопроса, на какой тип сейфа хотите пополнить.
        """
        logging.info(f'Режим задать вопрос, какой тип сейфа?')
        list_name: list = Safetypes.get_list()
        self._connect_telebot.view_keyboard('Выберите тип сейфа:', list_name=list_name)
        self._next_function.set(self._input_safe_type_check)
        self._question_yes_no: QuestionYesNo

    def _input_safe_type_check(self):
        """
        Режим  проверяет ответ пользователя, по типу сейфа.
        Если правильно выбран, запоминает выбранный тип сейфа.
        """
        logging.info(f'Режим проверить "{self._connect_telebot.message}" - это тип?')
        if Safetypes.check(self._connect_telebot.message):
            self._result.safe_type = self._connect_telebot.message
            self._input_safe_list()
        else:
            self._connect_telebot.send_text(f'Выбран неправильный тип сейфа  - {self._connect_telebot.message} .')
            self._question_yes_no = QuestionYesNo(self._connect_telebot, "Выбран неправильный тип сейфа.")
            self._wait_answer_repeat_safe_type()

    def _wait_answer_repeat_safe_type(self):
        b_working = self._question_yes_no.work()
        if b_working:
            self._next_function.set(self._wait_answer_repeat_safe_type)
            return
        result: bool = self._question_yes_no.result
        if result:
            self._input_safe_type_check()  # Повторить
        else:
            raise ExceptionChoiceSafe('Юзер отказался повторять. Он не выбрал тип сейфа.')

    def _input_safe_list(self):
        """
        Режим показать сейфы с типом self._task_rule.safe_type
        """
        logging.info(f'Режим показать сейфы с типом "{self._result.safe_type}"')
        safes_dict = ModelSafeuser.get_dict(self._connect_telebot.id_user, type_name=self._result.safe_type)
        if not safes_dict:
            safes_dict = {}
        safes_dict[self._MODE_ADD] = self._MODE_ADD
        self._dict_safes_user = safes_dict
        self._connect_telebot.view_keyboard('Выберите сейф:', dict_name=safes_dict)
        self._next_function.set(self._input_safe_list_check)

    def _input_safe_list_check(self):
        """
        Проверка какой сейф выбрали с типом self._task_rule.safe_type.
        Или переход на шаг создания нового сейфа с типом self._task_rule.safe_type.
        """
        if self._connect_telebot.message == self._MODE_ADD:
            self._create_safe_question()
        else:
            id_safe = self._dict_safes_user.get(self._connect_telebot.message)
            if id_safe:
                self._result.safe_name = self._connect_telebot.message
                self._result.id_safe_user = id_safe
                logging.info(f'Выбран сейф ID_safe_user:{self._result.id_safe_user} name:"{self._result.safe_name}"')
            else:
                self._connect_telebot.send_text(f'Такого сейфа "{self._connect_telebot.message}" нет в списке.')
                self._question_yes_no = QuestionYesNo(self._connect_telebot,
                                                      f'"{self._connect_telebot.message}" - сейфа нет в списке.')
                self._wait_answer_repeat_id_safe()

    def _wait_answer_repeat_id_safe(self):
        b_working = self._question_yes_no.work()
        if b_working:
            self._next_function.set(self._input_safe_list)
            return
        result: bool = self._question_yes_no.result
        if result:
            self._input_safe_type_check()  # Повторить
        else:
            raise ExceptionChoiceSafe('Юзер отказался выбирать сейф.')


    def _create_safe_question(self):
        """
        Вопрос - какое имя сейфа создавать?
        """
        logging.info(f'Режим создания сейфа с типом "{self._result.safe_type}"')
        self._connect_telebot.send_text(f'Введите название сейфа с типом - "{self._result.safe_type}":')
        self._next_function.set(self._create_safe_answer)

    def _create_safe_answer(self):
        """
        Создать новый сейф у юзера
        """
        logging.info(f'Режим проверки названия сейфа "{self._connect_telebot.message}"')
        message_str = self._connect_telebot.message.upper()
        id_safelist = ModelSafelist.command_create(message_str, self._result.safe_type)
        self._result.id_safe_user = ModelSafeuser.command_create(self._connect_telebot.id_user, id_safelist)
        self._result.safe_name = message_str
        self._connect_telebot.send_text(f'Добавлен новый сейф "{message_str}" с типом {self._result.safe_type}.')

    @property
    def result(self) -> ChoiceSafeResult:
        return self._result

    def work(self) -> bool:
        self._next_function.work()
        if not self._result:
            return True