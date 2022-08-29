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


class FromUser:
    def __init__(self, id_user: int):
        self._id_user: int = id_user

    @property
    def id(self) -> int:
        return self._id_user


class MessageType(Enum):
    KEY = 'KEY'
    VALUE = 'VALUE'
    LAST = 'LAST'
    NEXT = 'NEXT'
    ALL = 'ALL'
    TRIGER = 'TRIGER'
    NONE = 'NONE'


class NameKey(Enum):
    LAST = '<<'
    NEXT = '>>'
    NO = '|'

class Message:
    def __init__(self, id_user: int, text: str):
        self.from_user = FromUser(id_user)
        self.text = text


class ConnectTelebot:
    def __init__(self, telebot: TeleBot, id_user: int):
        self._telebot = telebot
        self._id_user = id_user
        self.message_id: int = 0
        self.message: str = ''
        self._message_id_prev: int = 0
        self._debug: bool = False
        self._ini_debug()
        self._keyboard = None

    def _ini_debug(self):
        try:
            id_programmer = os.getenv('ID_programmer')
            if str(self._id_user) == id_programmer:
                self._debug = True
        except Exception as err:
            logging.warning('Невозможно инициализировать id_programmer')

    def set_message(self, message: str, m_id: int):
        self._message_id_prev = self.message_id
        self.message_id = m_id
        self.message = message

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
            print('ConnectTelebot.view_keyboard_in')
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
            print('ConnectTelebot.view_keyboard_out')
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
            key = types.InlineKeyboardButton(text=text_key, callback_data=text_key)
            keyboard.row(key)  # добавляем кнопку задания
            if type_message != MessageType.VALUE:  # добавляем кнопки страниц
                key_last = types.InlineKeyboardButton(text=NameKey.LAST.value, callback_data=NameKey.LAST.value)
                key_next = types.InlineKeyboardButton(text=NameKey.NEXT.value, callback_data=NameKey.NEXT.value)
                key_no = types.InlineKeyboardButton(text=NameKey.NO.value, callback_data=NameKey.NO.value)
                if type_message == MessageType.LAST:
                    keyboard.row(key_last, key_no)
                elif type_message == MessageType.NEXT:
                    keyboard.row(key_no, key_next)
                elif type_message == MessageType.ALL:
                    keyboard.row(key_last, key_next)
            self._telebot.send_message(self._id_user, text=text_keyboard, reply_markup=keyboard)
        except Exception as err:
            raise ExceptionConnectTelebot(f'Ошибка создания клавиатуры - {self.view_keyboard_task.__name__}')

    def update_keyboard_task(self, task_list: list, message_type: MessageType):
        """
        Обновление клавиатуры для юзера, в режиме удаления task
        :param task_list:
        :param message_type:
        """
        keyboard = self._create_keyboard_task(task_list, message_type)
        self._telebot.edit_message_reply_markup(chat_id=self._id_user, message_id=self._message_id_prev,
                                                reply_markup=keyboard)

    def _create_keyboard_task(self, task_list: list, message_type: MessageType):
        """
        Создание списка кнопок для юзера, в режиме удаления task
        :param task_list:
        :param message_type:
        """
        keyboard = types.InlineKeyboardMarkup()
        count = 0
        for i in range(0, 2):
            key_1 = types.InlineKeyboardButton(text=task_list[i + count], callback_data=task_list[i + count])
            key_2 = types.InlineKeyboardButton(text=task_list[i + count + 1], callback_data=task_list[i + count] + 1)
            key_3 = types.InlineKeyboardButton(text=task_list[i + count + 2], callback_data=task_list[i + count] + 1)
            keyboard.row(key_1, key_2, key_3)
            count += 2
        key_last = types.InlineKeyboardButton(text=NameKey.LAST.value, callback_data=NameKey.LAST.value)
        key_next = types.InlineKeyboardButton(text=NameKey.NEXT.value, callback_data=NameKey.NEXT.value)
        key_no = types.InlineKeyboardButton(text=NameKey.NO.value, callback_data=NameKey.NO.value)
        if message_type == message_type.LAST:
            keyboard.row(key_last, key_no)
        elif message_type == message_type.NEXT:
            keyboard.row(key_no, key_next)
        elif message_type == message_type.ALL:
            keyboard.row(key_last, key_next)
        return keyboard


