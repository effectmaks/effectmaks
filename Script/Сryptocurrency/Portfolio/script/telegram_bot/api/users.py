import logging
from typing import Dict
from telebot import TeleBot
from ..controlBot import ControlBot
from .telegramApi import Message, ConnectTelebot, TypeMessage
from business_model.taskrule import TaskRule


class Users:
    """
    Класс пользователи контролирует многопользовательский режим.
    Каждый класс, это отдельный пользователь.
    """
    dict_users: Dict[int, 'Users'] = {}

    def __init__(self, botTelegram: TeleBot, id_user: int):
        self._id_user = id_user
        connect_telebot = ConnectTelebot(botTelegram, id_user)
        self.control_bot = ControlBot(connect_telebot)

    @classmethod
    def message_info(cls, bot_telegram: TeleBot, message: Message):
        """
        Обрабатывает сообщения юзера.
        Создает нового пользователя или обращается к существующему.
        :return:
        """
        logging.info('>||')
        user = cls.dict_users.get(message.id_user)
        if user:
            logging.info(f'Новое сообщение id_user:{message.id_user}')
        else:
            logging.info(f'Новый user_id:{message.id_user}')
            TaskRule.check_delete(message.id_user)  # Проверяет базу на наличие запущенных заданий и удаляет их
            user = Users(bot_telegram, message.id_user)
            cls.dict_users[message.id_user] = user
        try:
            logging.info('||>>>||')
            user.control_bot.new_message(message)
        except Exception as ex:
            logging.error(f'Серьезная ошибка в обработке данных {str(ex)}')
            cls.dict_users.pop(message.id_user, None)
        logging.info('||>')

    @classmethod
    def button_info(cls, bot_telegram: TeleBot, call):
        """
        Обрабатывает сообщения от нажатия кнопки юзера.
        Создает нового пользователя или обращается к существующему.
        :param bot_telegram:
        :param message:
        :return:
        """
        message = Message(id_user=call.from_user.id, text=call.data, id_message=call.message.id,
                          type_message=TypeMessage.KEYBOARD)
        Users.message_info(bot_telegram, message)
