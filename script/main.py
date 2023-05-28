import logging
import sys
import datetime
from logging.handlers import TimedRotatingFileHandler

import os
import time
from telebot import TeleBot
from dotenv import load_dotenv
from telegram_bot.api.users import Users
from telegram_bot.api.telegramApi import Message, TypeMessage

log_file = datetime.datetime.now().strftime("%Y_%m_%d") + ".log"

# Создание обработчика логов для Telebot и других модулей в один файл
handler = TimedRotatingFileHandler(f"logs/all_{log_file}", when="midnight", interval=1, backupCount=10)
handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
handler.setLevel(logging.DEBUG)
logging.getLogger().addHandler(handler)


def check_start_bot(bot_telegram: TeleBot):
    """
    Проверка, что бот запущен.
    Вызывает исключение если не удалось заполучить информацию от сервера
    :param bot_telegram:
    """
    user = bot_telegram.get_me()  # запрос об информации бота на сервер
    logging.info('Подключение TeleBot - успешно')  # не вызвано исключение, бот запущен


def start_bot():
    """
    Создание бота.
    Объявление объекта класс TeleBot.
    Создание прерываний по новому сообщению и нажатие на кнопку
    """
    logging.info('Команда подключить TeleBot')
    load_dotenv('.env')
    bot_telegram = TeleBot(os.getenv('API_token'))

    @bot_telegram.message_handler(content_types=['text'])
    def new_message(message_api):
        """
        Прерывание новое сообщение
        :param message_api: Объект сообщения от сервера
        """
        message = Message(id_user=message_api.from_user.id, text=message_api.text, id_message=message_api.id,
                          type_message=TypeMessage.TEXT)
        Users.message_info(bot_telegram, message)

    @bot_telegram.callback_query_handler(func=lambda call: True)
    def click_button(call):
        """
        Прерывание нажатие на кнопку в чате
        :param call: Объект сообщения от сервера
        """
        Users.button_info(bot_telegram, call)

    check_start_bot(bot_telegram)
    bot_telegram.polling(none_stop=True, interval=0)


if __name__ == '__main__':
    # Главный цикл программы
    while True:
        try:
            start_bot()
        except Exception as err:
            logging.error(f'Серьезная ошибка TelegramApi. {err}')
            logging.error(f'Попытаться запустить бот через 5 сек')
            time.sleep(5)  # пересоздать класс через 5 сек
