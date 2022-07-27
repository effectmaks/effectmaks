import logging
import sys
from base.coin import ModelCoin
from base.cash import ModelCash
from base.safeuser import ModelSafeuser

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

if __name__ == '__main__':
    logging.info('Наладка логирования')
    try:
        #ModelCoin.test_coin('SOL')
        #ModelCash.add_cash(1, 'ETH', 1.0, 10300.0)
        ModelSafeuser.test_safe(1, 2)
    except Exception as e:
        print(str(e))



