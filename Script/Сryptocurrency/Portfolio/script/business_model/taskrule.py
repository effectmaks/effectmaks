import logging
from datetime import datetime

from base.models.cash import ModelCash
from base.models.eventbank import ModelEventBank
from base.models.task import ModelTask, TaskStatus
from telegram_bot.api.commandsWork import CommandsWork


class ExceptionTaskList(Exception):
    def __init__(self, err_message: str = ''):
        logging.error(err_message)
        super().__init__(err_message)


class TaskRule:
    """
    Выполняет задание на заполнение базы данными
    """
    def __init__(self, id_user: int, command_type: str):
        logging.info(f'Создание задания. Тип: {command_type}')
        self._command_type: str = command_type
        self._id_user: int = id_user
        self.date_time: datetime = None
        self.safe_type: str = ""
        self.safe_name: str = ""
        self.id_safe_user: int = 0
        self.coin: str = ""
        self.amount: float = 0
        self.fee: float = 0
        self._id_task: int = 0
        self.comment: str = ""

    def run(self):
        logging.info(f'Команда выполнить задание. Тип: {self._command_type}')
        if self._command_type == CommandsWork.COMMAND_INPUT:
            try:
                desc = f"Добавить date_time:{self.date_time},  safe_name:{self.safe_name}, " \
                       f"id_safe_user:{self.id_safe_user}, coin:{self.coin}, amount:{self.amount}, fee:{self.fee}"
                self._id_task = ModelTask.create(id_user=self._id_user, task_type=self._command_type, desc=desc,
                                                 status=TaskStatus.RUN)
                id_cash_buy = ModelCash.add(id_safe_user=self.id_safe_user, date_time=self.date_time, coin=self.coin,
                              amount_buy=self.amount, price_buy_fiat=0, id_task=self._id_task)
                ModelEventBank.add(id_task=self._id_task, type=self._command_type, date_time=datetime.now(),
                                   id_cash_buy=id_cash_buy, fee=self.fee, comment=self.comment)
                ModelTask.set_completed_status(self._id_task)
                logging.info(f'Задание {CommandsWork.COMMAND_INPUT} выполнено')
            except Exception as err:
                logging.error(f'Задание {CommandsWork.COMMAND_INPUT} НЕ выполнено')
                self._task_delete(id_task_delete=self._id_task)
                raise ExceptionTaskList(f'Ошибка {CommandsWork.COMMAND_INPUT}: {err}')

    @classmethod
    def check_delete(cls, id_user: int = 0):
        """
        Удаляет из таблиц cash, event_bank записи, которые были запущены, но не завершены.
        Вызывается функция, когда скрипт был остановлен и авторизовался пользователь заново.
        :param id_user: ID юзера
        """
        try:
            logging.info('Проверить, есть ли запущенные задания и удалить их.')
            list_task_delete = ModelTask.get_list_run(id_user=id_user)
            if list_task_delete:
                logging.info(f'Есть задания которые нужно удалить в кол-ве - {len(list_task_delete)} шт.')
                for id_task_delete in list_task_delete:
                    cls._task_delete(id_task_delete)
        except Exception as err:
            logging.error(f'Критическая ошибка при удалении заданий у ID юзер:{id_user} - {str(err)}')

    @classmethod
    def _task_delete(cls, id_task_delete: int = 0):
        """
        Удалить из всех таблиц базы записи с запущенными заданиями.
        :param id_task_delete: ID задания для удаления
        """
        try:
            logging.info(f'!!!')
            logging.info(f'Удалить все записи задания ID:{id_task_delete}')
            ModelCash.delete_task_run(id_task=id_task_delete)
            ModelEventBank.delete_task_run(id_task=id_task_delete)
            ModelTask.set_delete_status(id_task_delete)
            logging.info(f'ID задание:{id_task_delete} успешно удалено.')
        except Exception as err:
            logging.error(f'Не удалось удалить все записи с ID_task: {id_task_delete} -  {str(err)}')




























