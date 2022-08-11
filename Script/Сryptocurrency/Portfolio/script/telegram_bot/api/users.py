import logging
from typing import Dict
from telebot import TeleBot
from ..controlBot import ControlBot
from .telegramApi import Message, ConnectTelebot
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
    def message_info(cls, bot_telegram: TeleBot, id_user: int, message_str: str):
        """
        Обрабатывает сообщения юзера.
        Создает нового пользователя или обращается к существующему.
        :param message_str:
        :param id_user:
        :param bot_telegram:
        :return:
        """
        logging.info('>>>||')
        user = cls.dict_users.get(id_user, None)
        if user:
            logging.info(f'Новое сообщение id_user:{id_user}')
        else:
            logging.info(f'Новый user_id:{id_user}')
            TaskRule.check_delete(id_user)  # Проверяет базу на наличие запущенных заданий
            user = Users(bot_telegram, id_user)
            cls.dict_users[id_user] = user
        try:
            user.control_bot.new_message(message_str)
        except Exception as ex:
            logging.error(f'Серьезная ошибка в обработке данных {str(ex)}')
            cls.dict_users.pop(id_user, None)
        logging.info('||>>>')

    @classmethod
    def button_info(cls, bot_telegram: TeleBot, call):
        """
        Обрабатывает сообщения от нажатия кнопки юзера.
        Создает нового пользователя или обращается к существующему.
        :param bot_telegram:
        :param message:
        :return:
        """
        #bot_telegram.delete_message(call.from_user.id, call.message.id)  # удалить все сообщение
        bot_telegram.edit_message_reply_markup(call.from_user.id, call.message.id)  # удалить клавиатуру
        bot_telegram.send_message(call.from_user.id, message.text)  # отправить текст выбранной кнопки
        Users.message_info(bot_telegram, call.from_user.id, call.data)
