import logging
from telebot import TeleBot, types


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
        self._telebot = telebot
        self._id_user = id_user
        self.message: str = ''

    def send_text(self, text_send: str):
        logging.info(f'Отправить текст юзеру ID {self._id_user}: "{text_send}"')
        self._telebot.send_message(self._id_user, text=text_send, disable_web_page_preview=True)
        logging.info('Отправлено')

    @property
    def id_user(self):
        return self._id_user

    def view_keyboard(self, text_keyboard: str, list_name: list = None, dict_name: dict = None):
        """
        Создание списка кнопок для юзера
        :param dict_text: Словарь с названиями кнопок
        :param text_keyboard: Вопрос для пользователя
        """
        keyboard = types.InlineKeyboardMarkup()  # клавиатура
        if list_name:
            for value in list_name:
                key = types.InlineKeyboardButton(text=value, callback_data=value)
                keyboard.add(key)  # добавляем кнопку
        else:
            for value in dict_name.keys():
                key = types.InlineKeyboardButton(text=value, callback_data=value)
                keyboard.add(key)  # добавляем кнопку
        self._telebot.send_message(self._id_user, text=text_keyboard, reply_markup=keyboard)

    def view_keyboard_yes_no(self, text_keyboard: str, const_yes: str, const_no: str):
        """
        Создание списка кнопок для юзера
        :param dict_text: Словарь с названиями кнопок
        :param text_keyboard: Вопрос для пользователя
        """

        key_yes = types.InlineKeyboardButton(text=const_yes, callback_data=const_yes)
        key_no = types.InlineKeyboardButton(text=const_no, callback_data=const_no)
        keyboard = types.InlineKeyboardMarkup()
        keyboard.row(key_yes, key_no)
        self._telebot.send_message(self._id_user, text=text_keyboard, reply_markup=keyboard)



