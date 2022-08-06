import sys
import logging
from business_model.taskrule import TaskRule, TaskModes
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("telegram_bot/debug.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

if __name__ == '__main__':
    task = TaskRule(task_type=TaskModes.BANK_INPUT,
                date_time=datetime.now(),
                id_user=481687938,
                safe_type='EXCHANGE',
                safe_name='OKEX',
                id_safe_user=1,
                coin='ETH',
                amount=1,
                fee=0.001)
    task.execute()
    task.check_delete(id_user=481687938)


