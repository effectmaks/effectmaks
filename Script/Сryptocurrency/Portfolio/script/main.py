import logging
import sys

import os
import time
from telebot import TeleBot
from dotenv import load_dotenv
from telegram_bot.api.users import Users

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("telegram_bot/debug.log"),
        logging.StreamHandler(sys.stdout)
    ]
)


def check_start_bot(bot_telegram: TeleBot):
    user = bot_telegram.get_me()  # запрос об информации бота на сервер
    logging.info('Подключение TeleBot - успешно')  # не вызвано исключение, бот запущен


def start_bot():
    logging.info('Команда подключить TeleBot')
    load_dotenv('telegram_bot/api/keys.env')
    bot_telegram = TeleBot(os.getenv('API_token'))

    @bot_telegram.message_handler(content_types=['text'])
    def new_message(message):
        Users.message_info(bot_telegram, message)

    @bot_telegram.callback_query_handler(func=lambda call: True)
    def click_button(call):
        Users.button_info(bot_telegram, call)

    check_start_bot(bot_telegram)
    bot_telegram.polling(none_stop=True, interval=0)


if __name__ == '__main__':
   while True:
        try:
            start_bot()
        except Exception as err:
            logging.error(f'Серьезная ошибка TelegramApi. {err}')
            logging.error(f'Попытаться запустить бот через 5 сек')
            time.sleep(5)  # пересоздать класс через 5 сек



