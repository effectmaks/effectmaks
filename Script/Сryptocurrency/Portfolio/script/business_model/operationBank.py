import logging

from business_model.modes.scriptBankInput import ScriptBankInput
from telegram_bot.api.commandsWork import CommandsWork
from telegram_bot.api.telegramApi import ConnectTelebot


class ExceptionOperationBank(Exception):
    def __init__(self, err_message: str = ''):
        logging.error(f'Класс {ExceptionOperationBank.__name__} - {err_message}')
        super().__init__(err_message)


class OperationBank:
    """
    Операции ввода, вывода и конвертации средств
    """
    def __init__(self, connect_telebot: ConnectTelebot, command_now: str):
        logging.info('Создание объекта OperationBank')
        self._command_now = command_now
        self._connect_telebot = connect_telebot
        self._script_bank_input = ScriptBankInput(self._connect_telebot)

    def work(self):
        """
        Работа класса, в зависимости от команды, опрашивает пользователя
        """
        if self._command_now == CommandsWork.COMMAND_INPUT:
            self._script_bank_input.work()
