import logging
from .api.telegramApi import ConnectTelebot


class ModesWork:
    COMMAND_START = '/start'
    COMMAND_HELP = '/help'


class ControlBot:
    """
    Выбор режима работы по команде, отправка сообщений юзеру
    """
    __NAME_BOT = 'CryptoFiatBot'

    def __init__(self, connect_telebot: ConnectTelebot):
        self.__connect_telebot: ConnectTelebot = connect_telebot

    def new_message(self, message):
        """
        Пришло сообщение от юзера
        :param message: Объект с текстом юзера
        """
        logging.info(f'Принято сообщение: {message.text}')
        if self._simple_mode(message):
            return

    def _simple_mode(self, message) -> bool:
        """
        Выпоняет команды /start и /help
        :param message: Объект текстом юзера
        :return: True выполнена команда
        """
        if message.text == ModesWork.COMMAND_START:
            self._send_text_bot_start()
            return True
        elif message.text == ModesWork.COMMAND_HELP:
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
        text_send = f'{self.__NAME_BOT} выполняет команды:'
        self.__connect_telebot.send_text(text_send)
