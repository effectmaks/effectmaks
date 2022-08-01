import logging
import sys
from base.coin import ModelCoin
from base.cash import ModelCash
from base.safeuser import ModelSafeuser

import os
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


if __name__ == '__main__':
    try:
        #ModelCoin.test('SOL')
        ModelSafeuser.test(1, 2)
        #ModelCash.add(1, 'ETH', 1.0, 10300.0)

    except Exception as e:
        print(str(e))

    load_dotenv('telegram_bot/api/keys.env')
    logging.info('Подключение TeleBot')
    bot_telegram = TeleBot(os.getenv('API_token'))
    logging.info('Подключение TeleBot - успешно')

    @bot_telegram.message_handler(content_types=['text'])
    def new_message(message):
        Users.message_info(bot_telegram, message)

    @bot_telegram.callback_query_handler(func=lambda call: True)
    def click_button(call):
        Users.button_info(bot_telegram, call)

    bot_telegram.polling(none_stop=True, interval=0)



