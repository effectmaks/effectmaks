import logging
from telegram_bot.api.telegramApi import ConnectTelebot
from base.safeuser import ModelSafeuser
from base.safelist import Safetypes
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

    def work(self, message_str: str):
        if self._work_next_function(message_str):  # функция выполнилась
            return
        if self._command_now == ModesWork.COMMAND_INPUT:
            self._input_exhange_type(message_str)

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
        :return: Выполнилась функция
        """
        if self._next_function:
            self._next_function(message_str)
            if not self._add_next_function:
                self._next_function = None
                self._add_next_function = False
            return True  # Выполнилась функция

    def _input_exhange_type(self, message_str: str):
        list_name: list = Safetypes.get_list()
        self._connect_telebot.view_keyboard('Выберите тип сейфа:', list_name=list_name)
        self._set_next_function(self._input_exhange_type_check)

    def _input_exhange_type_check(self, message_str: str):
        if Safetypes.check(message_str):
            self._input_exhange(message_str)
        else:
            self._connect_telebot.send_text('Выбран неправильный тип сейфа.')
            raise ExceptionOperationBank(f'Выбран не правильный тип сейфа - {message_str}')

    def _input_exhange(self, message_str: str):
        safes_dict = ModelSafeuser.get_dict(self._connect_telebot.id_user, type_name=message_str)
        if not safes_dict:
            safes_dict = {}
        safes_dict['ДОБАВИТЬ'] = 'ДОБАВИТЬ'
        self._connect_telebot.view_keyboard('Выберите сейф:', dict_name=safes_dict)
        self._set_next_function(self._input_exhange_check)

    def _input_exhange_check(self, message_str: str):
        self._connect_telebot.send_text(f'Введите 2')
