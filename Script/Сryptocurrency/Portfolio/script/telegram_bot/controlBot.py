import logging
from .api.telegramApi import ConnectTelebot
from business_model.operationBank import OperationBank
from .api.modesWork import ModesWork


class ControlBot:
    """
    Выбор режима работы по команде, отправка сообщений юзеру
    """
    __NAME_BOT = 'CryptoFiatBot'

    def __init__(self, connect_telebot: ConnectTelebot):
        self.__connect_telebot: ConnectTelebot = connect_telebot
        self._command_now = ModesWork.NONE
        self._operaton_bank = None

    def new_message(self, message_str: str):
        """
        Пришло сообщение от юзера
        :param message: Объект с текстом юзера
        """
        logging.info(f'Принято сообщение: {message_str}')
        if self._simple_mode(message_str):
            return
        elif self._input_mode(message_str):
            return

    def _input_mode(self, message_str: str) -> bool:
        """
        Режим пополнения средств на сейф из вне.
        """
        if message_str == ModesWork.COMMAND_INPUT:
            self._command_now = ModesWork.COMMAND_INPUT
            self._operaton_bank = OperationBank(self.__connect_telebot, self._command_now)

        if self._command_now == ModesWork.COMMAND_INPUT:
            try:
                self._operaton_bank.work(message_str)
            except Exception as err:
                logging.error(f'_input_mode: {str(err)}')
                self.__connect_telebot.send_text(f'Команда {self._command_now} завершена не успешно.')
                self._command_now = ModesWork.NONE
            return True
        return False

    def _simple_mode(self, message_str: str) -> bool:
        """
        Выпоняет команды /start и /help
        :param message: Объект текстом юзера
        :return: True выполнена команда
        """
        if message_str == ModesWork.COMMAND_START:
            self._send_text_bot_start()
            return True
        elif message_str == ModesWork.COMMAND_HELP:
            self._send_text_bot_help()
            return True
        return False

    def _send_text_bot_start(self):
        """
        Отправляет текст приветствия юзера
        :param id_user: ID пользователя
        """
        logging.info(f'Режим: СТАРТ')
        text_send = f'{self.__NAME_BOT} - твой крипто-портфель. Введите {ModesWork.COMMAND_HELP}.'
        self.__connect_telebot.send_text(text_send)

    def _send_text_bot_help(self):
        """
        Отправляет текст помощи юзеру
        :param id_user: ID пользователя
        """
        logging.info(f'Режим: Помощь')
        text_send = f'{self.__NAME_BOT} выполняет команды: \n' \
                    f'{ModesWork.COMMAND_INPUT} - пополнить счет'
        self.__connect_telebot.send_text(text_send)
