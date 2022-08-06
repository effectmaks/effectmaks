import logging
from datetime import datetime
from base.task import ModelTask, TaskStatus
from ..base.cash import ModelCash
from base.eventbank import ModelEventBank


class ExceptionTaskList(Exception):
    def __init__(self, err_message: str = ''):
        logging.error(err_message)
        super().__init__(err_message)


class TaskModes:
    BANK_INPUT = "BANK_INPUT"


class TaskRule:
    """
    Выполняет задание на заполнение базы данными
    """
    def __init__(self, task_type: str = "",
                       date_time: datetime = None,
                       id_user: int = 0,
                       safe_type: str = '',
                       safe_name: str = '',
                       id_safe_user: int = '',
                       coin: str = '',
                       amount: float = '',
                       fee: float  = ''):
        logging.info('Создание задания')
        self._task_type: str = task_type
        self._id_user: int = id_user
        self._date_time: datetime = date_time
        self._safe_type: str = safe_type
        self._safe_name: str = safe_name
        self._id_safe_user: int = id_safe_user
        self._coin: str = coin
        self._amount: float = amount
        self._fee: float = fee
        self._id_task: int

    def execute(self):
        logging.info('Команда выполнить задание')
        if self._task_type == TaskModes.BANK_INPUT:
            try:
                desc = f"Добавить date_time:{self._date_time},  safe_name:{self._safe_name}, " \
                       f"id_safe_user:{self._id_safe_user}, coin:{self._coin}, amount:{self._amount}, fee:{self._fee}"
                self._id_task = ModelTask.create(id_user=self._id_user, task_type=self._task_type, desc=desc,
                                                 status=TaskStatus.RUN)
                ModelCash.add(id_safe_user=self._id_safe_user, date_time=self._date_time, coin=self._coin,
                              amount_buy=self._amount, price_buy_fiat=0, id_task=self._id_task)
                logging.info(f'Задание {TaskModes.BANK_INPUT} выполнено')
            except Exception as err:
                logging.info(f'Задание {TaskModes.BANK_INPUT} НЕ выполнено')
                raise ExceptionTaskList(f'Ошибка {TaskModes.BANK_INPUT}: {err}')

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
            ModelTask.set_delete(id_task_delete)
            logging.info(f'ID задание:{id_task_delete} успешно удалено.')
        except Exception as err:
            logging.error(f'Не удалось удалить все записи с ID_task: {id_task_delete}')




























