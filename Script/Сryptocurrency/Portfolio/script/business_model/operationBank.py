import logging
from telegram_bot.api.telegramApi import ConnectTelebot
from base.safeuser import ModelSafeuser
from base.safelist import Safetypes, ModelSafelist
from telegram_bot.api.modesWork import ModesWork


class ExceptionOperationBank(Exception):
    def __init__(self, err_message: str = ''):
        logging.error(err_message)
        super().__init__(err_message)


class OperationBank:
    """
    Операции ввода, вывода и конвертации средств
    """
    def __init__(self, connect_telebot: ConnectTelebot, command_now: str):
        logging.info('Создание объекта OperationBank')
        self._command_now = command_now
        self._connect_telebot = connect_telebot
        self._next_function = None
        self._add_next_function = False
        self._choice_safe_type: str
        self._MODE_ADD_SAFE = 'ДОБАВИТЬ'
        self._dict_safes_user = {}
        self._choice_safe_name: str
        self._choice_id_safe_user: int

    def work(self, message_str: str):
        if self._work_next_function(message_str):  # функция выполнилась
            return
        if self._command_now == ModesWork.COMMAND_INPUT:
            self._input_safe_type()

    def _set_next_function(self, fnc):
        """
        Устанавливает следующая функция для вызова, когда придет новое сообщение
        :param fnc: Следующая функция для вызова
        """
        self._next_function = fnc
        self._add_next_function = True

    def _work_next_function(self, message_str: str) -> bool:
        """
        Если было назначена следующая функция, то нужно выполнить
        :param message_str: Текст сообщения пользователя
        :return:True - выполнилась функция
        """
        if self._next_function:
            self._next_function(message_str)
            if not self._add_next_function:
                self._next_function = None
                self._add_next_function = False
            return True  # Выполнилась функция

    def _input_safe_type(self):
        """
        Формирование вопроса, на какой тип сейфа хотите пополнить.
        """
        logging.info(f'Режим задать вопрос, какой тип сейфа?')
        list_name: list = Safetypes.get_list()
        self._connect_telebot.view_keyboard('Выберите тип сейфа:', list_name=list_name)
        self._set_next_function(self._input_safe_type_check)

    def _input_safe_type_check(self, message_str: str):
        """
        Проверяет ответ пользователя, по типу сейфа.
        Если правильно выбран, запоминает выбранный тип сейфа.
        :param message_str: Ответ юзера
        """
        logging.info(f'Режим проверить "{message_str}" - это тип?')
        if Safetypes.check(message_str):
            self._choice_safe_type = message_str
            self._input_safe_list()
        else:
            self._connect_telebot.send_text('Выбран неправильный тип сейфа.')
            raise ExceptionOperationBank(f'Выбран не правильный тип сейфа - {message_str}')

    def _input_safe_list(self):
        """
        Режим показать сейфы с типом self._choice_safe_type
        """
        logging.info(f'Режим показать сейфы с типом "{self._choice_safe_type}"')
        safes_dict = ModelSafeuser.get_dict(self._connect_telebot.id_user, type_name=self._choice_safe_type)
        if not safes_dict:
            safes_dict = {}
        safes_dict[self._MODE_ADD_SAFE] = self._MODE_ADD_SAFE
        self._dict_safes_user = safes_dict
        self._connect_telebot.view_keyboard('Выберите сейф:', dict_name=safes_dict)
        self._set_next_function(self._input_safe_list_check)

    def _input_safe_list_check(self, message_str: str):
        """
        Проверка какой сейф выбрали с типом self._choice_safe_type.
        Или переход на шаг создания нового сейфа с типом self._choice_safe_type.
        :param message_str: Ответ юзера
        """
        if message_str == self._MODE_ADD_SAFE:
            self._create_safe_question()
        else:
            id_safe = self._dict_safes_user.get(message_str)
            if id_safe:
                self._choice_safe_name = message_str
                self._choice_id_safe_user = id_safe
                logging.info(f'Выбран сейф ID_safe_user:{self._choice_id_safe_user} name:"{self._choice_safe_name}"')
                self._input_coin()
            else:
                self._connect_telebot.send_text(f'Такого сейфа "{message_str}" нет в списке.')
                raise ExceptionOperationBank(f'Пользователь выбрал сейф - "{message_str}", он не из списка.')

    def _create_safe_question(self):
        """
        Вопрос - какое имя сейфа создавать?
        :return:
        """
        logging.info(f'Режим создания сейфа с типом "{self._choice_safe_type}"')
        self._connect_telebot.send_text(f'Введите название сейфа с типом - "{self._choice_safe_type}":')
        self._set_next_function(self._create_safe_answer)

    def _create_safe_answer(self, message_str: str):
        """
        Создать новый сейф у юзера
        :param message_str:
        :return:
        """
        logging.info(f'Режим проверки названия сейфа "{message_str}"')
        message_str = message_str.upper()
        id_safe_list = ModelSafelist.command_create(message_str, self._choice_safe_type)
        self._choice_id_safe_user = ModelSafeuser.command_create(self._connect_telebot.id_user, id_safe_list)
        self._connect_telebot.send_text(f'Добавлен новый сейф "{message_str}" с типом {self._choice_safe_type}.')
        self._input_coin()

    def _input_coin(self):
        logging.info(f'Режим вопрос пользователю, какая монета?')
