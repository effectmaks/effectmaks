import logging
import sys
from decimal import Decimal
from datetime import datetime

from base.models.cash import Cash, ModelCash
from business_model.choice.folderChoiceFloat.questionAmount import TypesAnswerAmount
from business_model.taskrule import TaskRule
from telegram_bot.api.commandsWork import CommandsWork

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("telegram_bot/debug.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

if __name__ == '__main__':
    a_li = [117, 116]
    template: str = '%d.%m.%Y %H:%M:%S'
    date1 = datetime.strptime("10.06.2021 15:35:32", template)
    dict1 = ModelCash.dict_amount(id_safe_user=9, filter_coin_view="USD", list_cash_no_view=a_li,
                          filter_cash_date_before=date1)
    a=0


