import logging
from telegram_bot.api.telegramApi import ConnectTelebot
from base.safeuser import ModelSafeuser
from telegram_bot.api.modesWork import ModesWork


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
            self._step_exhange(message_str)

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

    def _input_exhange(self, message_str: str):
        self._model_safes_user = ModelSafeuser(self._connect_telebot.id_user)
        safes_dict = self._model_safes_user.get_dict()
        text_safes = ''
        for safe in safes_dict.values():
            text_safes += safe + ' '
        self._connect_telebot.send_text(f'Введите биржу из списка: {text_safes}')
        self._set_next_function(self._input_exhange_check)

    def _input_exhange_check(self, message_str: str):
        self._connect_telebot.send_text(f'Введите 2')
