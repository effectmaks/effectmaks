import logging
import sys
from base.coin import ModelCoin
from base.cash import ModelCash
from base.safeuser import ModelSafeuser
from base.eventbank import ModelEventBank
from base.cashsell import ModelCashSell


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
        #ModelSafeuser.test(1, 2)
        #id_cash = ModelCash.add(1, '01.08.22 10.00.00', 'ETH', 1.0, 10300.0)
        #id_cash_sell = ModelCashSell.add(1, '01.08.22 10.00.00', id_cash, 1.0, 10300.0)
        ModelEventBank.add(1, 'INT', '01.08.22 10.00.00', 20, 0, fee=0.32, comment='sdf8520')

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



