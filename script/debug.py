import logging
import sys
from decimal import Decimal
from datetime import datetime

from base.models.cash import Cash, ModelCash
from base.models.task import Task, ModelTask
from business_model.choice.choicedate import ChoiceDate
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
    d = ModelTask.get_dict_completed(481687938, 'input')


