import logging
from datetime import datetime

from peewee import TextField, IntegerField, DateTimeField, Model

from .sqlite.connectSqlite import ConnectSqlite, ExceptionSelect, ExceptionInsert


class TaskStatus:
    DELETED = "DELETED"
    RUN = "RUN"
    COMPLETED = "COMPLETED"


class Task(Model):
    """
    База данных таблица Заданий
    """
    id = IntegerField()
    date_time = DateTimeField(default=datetime.now())
    id_user = IntegerField()
    type = TextField()
    desc = TextField()
    status = TextField()

    class Meta:
        table_name = 'task'
        database = ConnectSqlite.get_connect()


class ModelTask:
    __name_model = 'task'

    @classmethod
    def create(cls, id_user: int = 0, task_type: str = "", desc: str = "", status: str = "") -> int:
        """
        Добавляет задание в базу
        :param id_user: ID юзера
        :param task_type: Тип
        :param desc: Описание задачи
        :return: ID задания
        """
        logging.info('Команда добавить задание в базу')
        try:
            id_task = Task.create(id_user=id_user, type=task_type, desc=desc, status=status)
            logging.info(f'Добавлено задание ID:{id_task} status:{status}')
            return id_task
        except Exception as err:
            raise ExceptionInsert(cls.__name_model, str(err))

    @classmethod
    def get_list_run(cls, id_user: int = 0) -> list:
        """
        Возвращает лист с ID в статусе TaskStatus.RUN
        :param id_user: ID юзера
        :return: Лист с ID task
        """
        logging.info(f'Команда выгрузить все записи у ID юзера:{id_user} в статусе TaskStatus.RUN')
        try:
            list_out = []
            list_task = Task.select().where(Task.id_user == id_user, Task.status == TaskStatus.RUN)
            for task in list_task:
                list_out.append(task.id)
            if list_out:
                logging.info(f'Нужно удалить запущенные задания.')
            else:
                logging.info(f'Запущенных заданий нет.')
            return list_out
        except Exception as err:
            raise ExceptionSelect(cls.__name_model, str(err))

    @classmethod
    def set_delete_status(cls, id_task: int):
        """
        Помечает статус задания с _id_task как TaskStatus.DELETED
        :param id_user: ID юзера
        """
        cls._set_status(id_task=id_task, type_status=TaskStatus.DELETED)

    @classmethod
    def set_run_status(cls, id_task: int):
        """
        Помечает статус задания с _id_task как TaskStatus.DELETED
        :param id_user: ID юзера
        """
        cls._set_status(id_task=id_task, type_status=TaskStatus.RUN)

    @classmethod
    def set_completed_status(cls, id_task: int):
        """
        Помечает статус задания с _id_task как TaskStatus.DELETED
        :param id_user: ID юзера
        """
        cls._set_status(id_task=id_task, type_status=TaskStatus.COMPLETED)

    @classmethod
    def _set_status(cls, id_task: int, type_status: str):
        """
        Помечает статус задания с _id_task как type_status
        :param id_user: ID юзера
        :param type_status: Тип статуса
        """
        logging.info(f'Команда пометить ID_задание:{id_task} - статус:{type_status}')
        try:
            command_update = Task.update(status=type_status).where(Task.id == id_task)
            command_update.execute()
            logging.info(f'Успешно обновлен статус задания.')
            return id_task
        except Exception as err:
            raise ExceptionInsert(cls.__name_model, str(err))


