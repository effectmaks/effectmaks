import logging
from datetime import datetime
from typing import Dict
from decimal import Decimal

from peewee import TextField, IntegerField, DateTimeField, Model

from base.models.eventbank import EventBank
from base.sqlite.connectSqlite import ConnectSqlite, ExceptionSelect, ExceptionInsert
from business_model.choice.choicedate import ChoiceDate


class TaskViewItem:
    def __init__(self):
        self.dict_task = {}
        self.date_last: datetime = None
        self.date_next: datetime = None

    def __copy__(self):
        task = TaskViewItem()
        task.dict_task = self.dict_task.copy()
        task.date_last = self.date_last
        task.date_next = self.date_next
        return task


class TaskStatus:
    DELETED = "DELETED"
    RUN = "RUN"
    COMPLETED = "COMPLETED"


class Task(Model):
    """
    База данных таблица Заданий
    """
    id = IntegerField()
    date_time = DateTimeField()
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
    def create(cls, id_user: int = 0, task_type: str = "", desc: str = "", status: str = "", date_time: datetime = None) -> int:
        """
        Добавляет задание в базу
        :param id_user: ID юзера
        :param task_type: Тип
        :param desc: Описание задачи
        :return: ID задания
        """
        logging.info('Команда добавить задание в базу')
        try:
            id_task = Task.create(id_user=id_user, type=task_type, desc=desc, status=status, date_time=date_time)
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
    def get_dict_completed(cls, id_user: int = 0, task_type: str = "",
                           task_view_item: TaskViewItem = None,
                           date_time_next: datetime = None,
                           date_time_last: datetime = None,
                           count_limit: int = 6):
        """
        Возвращает лист с ID в status = "COMPLETED"
        :param count_limit:
        :param date_time:
        :param task_type:
        :param id_user: ID юзера
        :return: Словарь с ID task Task.id, EventBank.comment, Task.date_time, Task.type, Task.desc
        """
        date_time_filter = ""
        if date_time_next and date_time_last:
            date_time_filter = f'and task.date_time <= "{date_time_next}" and task.date_time >= "{date_time_last}"'
        elif date_time_next:
            date_time_filter = f'and task.date_time > "{date_time_next}"'
        try:
            logging.info('Возвращает лист с ID в status = "COMPLETED"')
            connect = ConnectSqlite.get_connect()
            task_list = connect.execute_sql('select task.id, task.date_time, task.desc, task.type, eventbank.comment '
                                            'from task '
                                            'join eventbank '
                                            'on eventbank.id_task = task.id '
                                            'where status = "COMPLETED" and task.id_user = {} '
                                            'and task.type = "{}" '
                                            '{}'
                                            'order by task.date_time desc limit {}'.
                                            format(id_user,
                                                   task_type,
                                                   date_time_filter,
                                                   count_limit))
            if task_list:
                date_last: datetime = None
                for task in task_list:
                    task_view_item.dict_task[task[0]] = cls.task_desc(task[0], task[1], task[3], task[2], task[4])
                    date_last = task[1]
                    if not task_view_item.date_next:
                        task_view_item.date_next = task[1]
                task_view_item.date_last = date_last
                logging.info('Запрос выполнен')
            else:
                logging.info(f'В таблице {cls.__name_model} у сейфа ID:{id_user} нет выполненных статусов '
                             f'с типом {task_type}.')
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
        Помечает статус задания с _id_task как TaskStatus.RUN
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

    @classmethod
    def desc_in_or_out(self, znak: str, safe_name: str,  coin: str, amount: Decimal, fee: Decimal, type_command: str = '',
                        id_task: int = 0, date_time: str = '', comment: str = '') -> str:
        desc_task = ''
        if id_task:
            desc_task = f'#{id_task}\n'
        desc_date_time = ''
        if date_time:
            desc_date_time = f'{ChoiceDate.convert_to_str(date_time)}\n'
        desc_type_command = ''
        if type_command:
            desc_type_command = f'{type_command}\n'
        desc_comment = ''
        if comment:
            desc_comment = f'\n"{comment}"'
        return f'{desc_task}{desc_date_time}{desc_type_command}{znak} {safe_name} {coin}:{amount}\nfee: {fee}{desc_comment}'

    @classmethod
    def desc_convertation_transfer(self, coin_sell: str, amount_sell: Decimal, coin_buy: str, amount_buy: Decimal,
                           type_command: str = '', id_task: int = 0, date_time: str = '',
                           comment: str = '', safe_sell: str = '', safe_buy: str = '', fee: Decimal = None) -> str:
        desc_task = ''
        if id_task:
            desc_task = f'#{id_task}\n'
        desc_date_time = ''
        if date_time:
            desc_date_time = f'{ChoiceDate.convert_to_str(date_time)}\n'
        desc_type_command = ''
        if type_command:
            desc_type_command = f'{type_command}\n'
        desc_comment = ''
        if comment:
            desc_comment = f'\n"{comment}"'
        desc_safe_sell = ''
        if safe_sell:
            desc_safe_sell = f'{safe_sell}'
        desc_safe_buy = ''
        if safe_buy:
            desc_safe_buy = f'{safe_buy}'
        desc_fee = ''
        if fee:
            desc_fee = f'fee: {fee}\n'
        return f'{desc_task}{desc_date_time}{desc_type_command}' \
               f'- {desc_safe_sell} {coin_sell}:{amount_sell}\n+ {desc_safe_buy} {coin_buy}:{amount_buy}\n' \
               f'{desc_fee}{desc_comment}'

    @classmethod
    def task_desc(self, task_id: int, date_time: str, task_type: str, desc: str, comment: str) -> str:
        desc_date_time = f'{ChoiceDate.convert_to_str(date_time)}'
        return f'# {task_id}\n{desc_date_time}\nКоманда: {task_type}\n' \
               f'{desc}\n"{comment}"'

    @classmethod
    def get_info(cls, id_task: int) -> str:
        """
        Команда выгрузить инфо ID_задания:{id_task}
        :param id_task: ID задания
        :return: Инфо задания
        """

        logging.info(f'Команда выгрузить инфо ID_задания:{id_task}.')
        try:
            items = Task.select(Task.id, EventBank.comment, Task.date_time, Task.type, Task.desc).join(EventBank, on=(EventBank.id_task == Task.id)).where(Task.id == id_task)
            info_str = ""
            for item in items:
                info_str = cls.task_desc(item.id, item.date_time, item.type, item.desc, item.eventbank.comment)
            logging.info(f'Успешно выгружено инфо.')
            return info_str
        except Exception as err:
            raise ExceptionSelect(cls.__name_model, str(err))

    @classmethod
    def get_dict_addiction(cls, id_task: int) -> Dict[int, str]:
        """
        Выгрузить зависимые от ID_задания:{id_task}
        :param id_task: ID задания
        :return: Словарь с описанием заданий
        """

        logging.info(f'Команда выгрузить инфо ID_задания:{id_task}.')
        dict_out: Dict[int, str] = {}
        try:
            connect = ConnectSqlite.get_connect()
            task_list = connect.execute_sql('SELECT c_s.id_task from eventbank as ev_bank '
                                            'join cashsell as c_s '
                                            'on c_s.id_cash = ev_bank.id_cash_buy '
                                            'and not c_s.id_task = ev_bank.id_task '
                                            'where ev_bank.id_task = {}'.
                                            format(id_task))

            if task_list:
                for task in task_list:
                    info = cls.get_info(task[0])
                    dict_out[task[0]] = info
            return dict_out
        except Exception as err:
            raise ExceptionSelect(cls.__name_model, str(err))



