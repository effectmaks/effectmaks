import logging
from telegram_bot.api.telegramApi import ConnectTelebot
from base.safeuser import ModelSafeuser
from telegram_bot.api.modesWork import ModesWork


class StepsModeInput:
    STOP = 'STOP'
    EXCHANGE = 'EXCHANGE'
    EXCHANGE_CHECK = 'EXCHANGE_CHECK'


class OperationBank:
    """
    Операции ввода, вывода и конвертации средств
    """
    def __init__(self, connect_telebot: ConnectTelebot, command_now: str):
        logging.info('Создание объекта OperationBank')
        self._command_now = command_now
        if  self._command_now == ModesWork.COMMAND_INPUT:
            self._step_now = StepsModeInput.EXCHANGE
        self._connect_telebot = connect_telebot

    def work(self, message_str: str):
        if self._command_now == ModesWork.COMMAND_INPUT and self._step_now == StepsModeInput.EXCHANGE:
            self._model_safes_user = ModelSafeuser(self._connect_telebot.id_user)
            safes_dict = self._model_safes_user.get_dict()
            text_safes = ''
            for safe in safes_dict.values():
                text_safes += safe + ' '
            self._connect_telebot.send_text(f'Введите биржу из списка: {text_safes}')
