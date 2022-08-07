import logging
import sys
from datetime import datetime
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
    TaskRule.check_delete(id_user=481687938)
    task = TaskRule(command_type=CommandsWork.COMMAND_INPUT)
    task.date_time = datetime.now()
    task.id_user = 481687938
    task.safe_type = 'EXCHANGE'
    task.safe_name = 'OKEX'
    task.id_safe_user = 1
    task.coin = 'ETH'
    task.amount = 1
    task.fee = 0.001
    task.comment = '1234'
    task.run()


