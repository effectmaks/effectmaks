import logging

from business_model.modes.scriptBankConvertation import ScriptBankConvertation
from business_model.modes.scriptBankInput import ScriptBankInput
from business_model.modes.scriptBankOutput import ScriptBankOutput
from business_model.modes.scriptCoinTransfer import ScriptCoinTransfer
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
        logging.info(f'Создание объекта {OperationBank.__name__}')
        self._command_now = command_now
        self._connect_telebot = connect_telebot
        self._script_bank_input = ScriptBankInput(self._connect_telebot)
        self._script_bank_output = ScriptBankOutput(self._connect_telebot)
        self._script_bank_convertation = ScriptBankConvertation(self._connect_telebot)
        self._script_coin_transfer = ScriptCoinTransfer(self._connect_telebot)

    def work(self):
        """
        Работа класса, в зависимости от команды, опрашивает пользователя
        """
        if self._command_now == CommandsWork.COMMAND_INPUT:
            self._script_bank_input.work()
        elif self._command_now == CommandsWork.COMMAND_OUTPUT:
            self._script_bank_output.work()
        elif self._command_now == CommandsWork.COMMAND_CONVERTATION:
            self._script_bank_convertation.work()
        elif self._command_now == CommandsWork.COMMAND_CONVERTATION:
            self._script_bank_convertation.work()
        elif self._command_now == CommandsWork.COMMAND_COIN_TRANSFER:
            self._script_coin_transfer.work()
