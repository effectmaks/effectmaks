import logging
import sys
from base.coin import ModelCoin
from base.cash import ModelCash
from base.safeuser import ModelSafeuser
from base.eventbank import ModelEventBank
from base.cashsell import ModelCashSell
from base.safelist import ModelSafelist, Safetypes

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
    try:
        #ModelCoin.test('SOL')
        #ModelSafeuser.test(1, 2)
        #id_cash = ModelCash.add(1, '01.08.22 10.00.00', 'ETH', 1.0, 10300.0)
        #id_cash_sell = ModelCashSell.add(1, '01.08.22 10.00.00', id_cash, 1.0, 10300.0)
        #ModelEventBank.add(1, 'INT', '01.08.22 10.00.00', 20, 0, fee=0.32, comment='sdf8520')
        ModelSafelist.command_create('ETH', Safetypes.EXCHANGE)

    except Exception as e:
        print(str(e))

    while True:
        try:
            start_bot()
        except Exception as err:
            logging.error(f'Серьезная ошибка TelegramApi. {err}')
            logging.error(f'Попытаться запустить бот через 5 сек')
            time.sleep(5)  # пересоздать класс через 5 сек



