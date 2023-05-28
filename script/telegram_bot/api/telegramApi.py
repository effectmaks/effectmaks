import logging
import os
from enum import Enum
from telebot import TeleBot, types


class ExceptionConnectTelebot(Exception):
    def __init__(self, err_message: str = ''):
        logging.error(f'Класс {ExceptionConnectTelebot.__name__} - {err_message}')
        super().__init__(err_message)


class ExceptionTelegramApi(Exception):
    def __init__(self, err_message: str = ''):
        logging.error(f'Класс {ExceptionTelegramApi.__name__} - {err_message}')
        super().__init__(err_message)


class TypeMessage(Enum):
    KEYBOARD = 1
    TEXT = 2


class MessageType(Enum):
    KEY = 'KEY'
    VALUE = 'VALUE'
    LAST = 'LAST'
    NEXT = 'NEXT'
    ALL = 'ALL'
    TRIGER = 'TRIGER'
    NONE = 'NONE'


class NameKey(Enum):
    NEXT = 'ПОКАЗАТЬ ЕЩЁ'


class Message:
    def __init__(self, id_user: int, text: str, id_message: int, type_message: TypeMessage):
        self.id_user = id_user
        self.text = text
        self.id = id_message
        self.type = type_message


class ConnectTelebot:
    def __init__(self, telebot: TeleBot, id_user: int):
        self._telebot = telebot
        self._id_user = id_user
        self._id_message: int = 0
        self._message: str = ''
        self._message_id_prev: int = 0
        self._debug: bool = False
        # self._ini_debug()
        self._keyboard = None
        self.work: bool = False

    @property
    def message(self):
        return self._message
        
    def _ini_debug(self):
        try:
            id_programmer = os.getenv('ID_PROGRAMMER')
            if str(self._id_user) == id_programmer:
                self._debug = True
        except Exception as err:
            logging.warning('Невозможно инициализировать id_programmer')

    def set_message(self, message: Message):
        self._message_id_prev = self._id_message
        self._id_message = message.id
        self._message = message.text
        self._type_message = message.type

    @property
    def debug(self) -> bool:
        return self._debug

    def send_text(self, text_send: str):
        logging.info(f'Отправить текст юзеру ID {self._id_user}.')
        self._telebot.send_message(self._id_user, text=text_send, disable_web_page_preview=True)
        logging.info('Отправлено')

    @property
    def id_user(self) -> int:
        return self._id_user

    def view_keyboard(self, text_keyboard: str, list_view: list = None, dict_view: dict = None,
                      type_message: MessageType = MessageType.VALUE):
        """
        Создание списка кнопок для юзера
        :param dict_text: Словарь с названиями кнопок
        :param text_keyboard: Вопрос для пользователя
        """
        try:
            if list_view:
                logging.info(f'Показать клавиатуру {text_keyboard}-{list_view}')
            else:
                logging.info(f'Показать клавиатуру {text_keyboard}-{dict_view.keys()}')
            keyboard = types.InlineKeyboardMarkup()  # клавиатура
            if list_view:
                for value in list_view:
                    key = types.InlineKeyboardButton(text=value, callback_data=value)
                    keyboard.add(key)  # добавляем кнопку
            else:
                for key, value in dict_view.items():
                    if MessageType.VALUE == type_message:
                        value = key
                    keyboard_item = types.InlineKeyboardButton(text=value, callback_data=key)
                    keyboard.add(keyboard_item)  # добавляем кнопку
            self._telebot.send_message(self._id_user, text=text_keyboard, reply_markup=keyboard)
        except Exception as err:
            raise ExceptionConnectTelebot(f'Ошибка создания клавиатуры - {self.view_keyboard.__name__}')

    def view_keyboard_yes_no(self, text_keyboard: str, const_yes: str, const_no: str):
        """
        Создание списка кнопок для юзера
        :param dict_text: Словарь с названиями кнопок
        :param text_keyboard: Вопрос для пользователя
        """
        try:
            key_yes = types.InlineKeyboardButton(text=const_yes, callback_data=const_yes)
            key_no = types.InlineKeyboardButton(text=const_no, callback_data=const_no)
            keyboard = types.InlineKeyboardMarkup()
            keyboard.row(key_yes, key_no)
            self._telebot.send_message(self._id_user, text=text_keyboard, reply_markup=keyboard)
        except Exception as err:
            raise ExceptionConnectTelebot(f'Ошибка создания клавиатуры - {self.view_keyboard_yes_no.__name__}')

    def view_keyboard_task(self, text_keyboard: str, text_key: str, type_message: MessageType):
        """
        Показать клавиатуру для юзера, в режиме удаления task
        :param task_list:
        :param message_type:
        """
        try:
            keyboard = types.InlineKeyboardMarkup()
            if text_key != "":
                key = types.InlineKeyboardButton(text=text_key, callback_data=text_key)
                keyboard.row(key)  # добавляем кнопку задания
                self._telebot.send_message(self._id_user, text=text_keyboard, reply_markup=keyboard)
            if type_message != MessageType.VALUE:  # добавляем кнопки страниц
                keyboard = types.InlineKeyboardMarkup()
                key_next = types.InlineKeyboardButton(text=NameKey.NEXT.value, callback_data=NameKey.NEXT.value)
                keyboard.row(key_next)
                self._telebot.send_message(self._id_user, text="Показать дополнительные задания?", reply_markup=keyboard)

        except Exception as err:
            raise ExceptionConnectTelebot(f'Ошибка создания клавиатуры - {self.view_keyboard_task.__name__}')
        
    def delete_keyboard(self):
        """
        Удалить клавиатуру у юзера
        """
        if self._type_message == TypeMessage.KEYBOARD:
            # bot_telegram.delete_message(call.from_user.id, call.message.id)  # удалить все сообщение
            self._telebot.edit_message_reply_markup(self._id_user, self._id_message)  # удалить клавиатуру
            self._telebot.send_message(self._id_user, self._message)  # отправить текст выбранной кнопки

