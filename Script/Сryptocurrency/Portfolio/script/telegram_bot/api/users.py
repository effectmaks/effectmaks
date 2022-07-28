import logging
from typing import Dict
from telebot import TeleBot
from ..controlBot import ControlBot
from .telegramApi import Message, ConnectTelebot


class Users:
    """
    Класс пользователи контролирует многопользовательский режим.
    Каждый класс, это отдельный пользователь.
    """
    dict_users: Dict[str, 'Users'] = {}

    def __init__(self, botTelegram: TeleBot, id_user: int):
        self._id_user = id_user
        connect_telebot = ConnectTelebot(botTelegram, id_user)
        self.control_bot = ControlBot(connect_telebot)

    @classmethod
    def message_info(cls, bot_telegram: TeleBot, message):
        """
        Обрабатывает сообщения юзера.
        Создает нового пользователя или обращается к существующему.
        :param bot_telegram:
        :param message:
        :return:
        """
        user = cls.dict_users.get(message.from_user.id, None)
        if user:
            logging.info(f'Новое сообщение id_user:{message.from_user.id}')
        else:
            logging.info(f'Новый user_id:{message.from_user.id}')
            user = Users(bot_telegram, message.from_user.id)
            cls.dict_users[message.from_user.id] = user
        try:
            user.control_bot.new_message(message)
        except Exception as ex:
            logging.error(f'Серьезная ошибка в обработке данных {str(ex)}')
            cls.dict_users.pop(message.from_user.id, None)

    @classmethod
    def button_info(cls, bot_telegram: TeleBot, call):
        """
        Обрабатывает сообщения от нажатия кнопки юзера.
        Создает нового пользователя или обращается к существующему.
        :param bot_telegram:
        :param message:
        :return:
        """
        message = Message(id=call.from_user.id, text=call.data)
        bot_telegram.edit_message_reply_markup(message.from_user.id, call.message.id)  # удалить клавиатуру
        bot_telegram.send_message(call.from_user.id, message.text)  # отправить текст выбранной кнопки
        Users.message_info(bot_telegram, message)
