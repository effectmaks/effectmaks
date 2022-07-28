import logging
from telebot import TeleBot


class ExceptionTelegramApi(Exception):
    def __init__(self, err_message: str = ''):
        logging.error(err_message)
        super().__init__(err_message)


class FromUser:
    def __init__(self, id_user: int):
        self._id_user: int = id_user

    @property
    def id(self) -> int:
        return self._id_user


class Message:
    def __init__(self, id_user: int, text: str):
        self.from_user = FromUser(id_user)
        self.text = text


class ConnectTelebot:
    def __init__(self, telebot: TeleBot, id_user: int):
        self.__telebot = telebot
        self.__id_user = id_user

    def send_text(self, text_send: str):
        logging.info(f'Отправить текст юзеру ID {self.__id_user}: "{text_send}"')
        self.__telebot.send_message(self.__id_user, text=text_send, disable_web_page_preview=True)
        logging.info('Отправлено')





