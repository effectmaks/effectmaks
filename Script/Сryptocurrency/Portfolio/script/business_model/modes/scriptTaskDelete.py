import logging
from datetime import datetime

from base.models.task import ModelTask, TaskViewItem
from business_model.helpers.nextfunction import NextFunction
from business_model.helpers.questionYesNo import QuestionYesNo
from business_model.taskrule import TaskRule
from telegram_bot.api.commandsWork import CommandsWork
from telegram_bot.api.telegramApi import ConnectTelebot, MessageType, NameKey


class ExceptionScriptTaskDelete(Exception):
    def __init__(self, err_message: str = ''):
        logging.error(f'Класс {ExceptionScriptTaskDelete.__name__} - {err_message}')
        super().__init__(err_message)


class ScriptTaskDelete:
    """
        Операция конвертации средств
    """

    def __init__(self, connect_telebot: ConnectTelebot):
        logging.info('Создание объекта ScriptTaskDelete')
        self._connect_telebot = connect_telebot
        self._next_function = NextFunction(ScriptTaskDelete.__name__)
        self._next_function.set(self._choice_type_command)
        self._question_yes_no: QuestionYesNo
        self._choice_command: str = ""
        self._choice_id_task: int = 0
        self._message_type: MessageType = MessageType.NONE
        self._message_type_triger: MessageType = MessageType.NONE
        self._task_view_item_triger: TaskViewItem = None  # сохраняет предыдущий словарь заданий, если достиг конца повторить вывод
        self._command_view: MessageType = MessageType.NONE

    def work(self):
        """
        Работа класса, в зависимости от команды, опрашивает пользователя
        """
        if self._next_function.work():  # функция выполнилась
            return

    def _choice_type_command(self):
        """
        Режим показать список команд
        """
        logging.info(f'Режим показать список команд')
        self._connect_telebot.view_keyboard('Выберите команду задания:', list_view=CommandsWork.get_list_operations())
        self._next_function.set(self._choice_type_command_check)

    def _choice_type_command_check(self):
        """
        Режим  проверяет ответ пользователя, по типу список команд
        """
        logging.info(f'Режим проверить "{self._connect_telebot.message}" - это команда?')
        if self._connect_telebot.message in CommandsWork.get_list_operations():
            self._choice_command = self._connect_telebot.message
            logging.info('Выбран _choice_command')
            self._view_list_task()
        else:
            self._error_choice_type_command_check()

    def _error_choice_type_command_check(self):
        """
        Пользователь выбрал не из списка команды
        """
        self._question_yes_no = QuestionYesNo(self._connect_telebot, f"Нет в списке команды - "
                                                                     f"{self._connect_telebot.message}.")
        self._next_function.set(self._wait_answer_choice_type_command)

    def _wait_answer_choice_type_command(self):
        """
        Ожидание будет ли повторять выбор команды
        """
        logging.info(f'Ожидание будет ли повторять выбор команды')
        b_working = self._question_yes_no.work()
        if b_working:
            self._next_function.set(self._wait_answer_choice_type_command)
            return
        result: bool = self._question_yes_no.result
        if result:
            self._choice_type_command_check()  # Повторить
        else:
            raise ExceptionScriptTaskDelete('Юзер отказался повторять. Он не выбрал команду.')

    def _view_list_task(self):
        """
        Режим вывести список заданий
        """
        logging.info(f'Режим вывести список заданий')
        date_time_next = None
        date_time_last = None
        if self._command_view == MessageType.NEXT:
            date_time_next = self._task_view_item_triger.date_next
        elif self._command_view == MessageType.LAST:
            date_time_next = self._task_view_item_triger.date_next
            date_time_last = self._task_view_item_triger.date_last

        if self._command_view == MessageType.TRIGER:
            task_view_item = self._task_view_item_triger
            self._message_type = self._message_type_triger
        else:
            task_view_item = TaskViewItem()
            ModelTask.get_dict_completed(self._connect_telebot.id_user,
                                         task_type=self._choice_command,
                                         task_view_item=task_view_item,
                                         date_time_next=date_time_next,
                                         date_time_last=date_time_last)

        if not task_view_item and self._message_type == MessageType.NONE:
            self._connect_telebot.send_text(f'Нет заданий с типом: {self._choice_command}.')
            raise ExceptionScriptTaskDelete(f'У юзера нет заданий с типом: {self._choice_command}.')
        elif not task_view_item and self._command_view == MessageType.NEXT:
            # Крайняя правая страница
            task_view_item = self._task_view_item_triger
            self._message_type = MessageType.LAST
        elif not task_view_item and self._command_view == MessageType.LAST:
            # Крайняя левая страница
            task_view_item = self._task_view_item_triger
            self._message_type = MessageType.NEXT

        self._connect_telebot.send_text("Список заданий:")
        self._message_type = MessageType.ALL
        for item in task_view_item.dict_task.values():
            self._connect_telebot.send_text(item)
        list_m: list = []
        for key in task_view_item.dict_task.keys():
            list_m.append(key)


        self._message_type = MessageType.NEXT
        self._connect_telebot.view_keyboard_task(list_m, message_type=self._message_type)
        self._task_view_item_triger = task_view_item.__copy__()
        self._message_type_triger = self._message_type

        self._next_function.set(self._view_list_task_check)

    def _view_list_task_check(self):
        """
        Режим проверяет ответ пользователя, по выбранному заданию
        """
        logging.info(f'Режим проверить "{self._connect_telebot.message}" - это ID задания?')
        if self._connect_telebot.message == NameKey.NO.value:  # юзер нажал на точку
            self._command_view = MessageType.TRIGER
            self._view_list_task()
            self._next_function.set(self._view_list_task_check)
            return
        elif self._connect_telebot.message == NameKey.NEXT.value:  # юзер нажал на следующее
            self._command_view = MessageType.NEXT
            self._view_list_task()
        elif self._connect_telebot.message == NameKey.LAST.value:  # юзер нажал на предыдущее
            self._command_view = MessageType.LAST
            self._view_list_task()

        if not self._connect_telebot.message.isdecimal():
            self._error_view_list_task()

        if int(self._connect_telebot.message) in self._task_view_item.keys():
            self._choice_id_task = int(self._connect_telebot.message)
            logging.info('Выбран _choice_id_task')
            self._choice_question_delete()
        else:
            self._error_view_list_task()

    def _error_view_list_task(self):
        """
        Пользователь не выбрал из списка, или ввел что то другое
        """
        self._question_yes_no = QuestionYesNo(self._connect_telebot,
                                              f'Нет в списке задания ID - {self._connect_telebot.message}.')
        self._next_function.set(self._wait_view_list_task)

    def _wait_view_list_task(self):
        """
        Ожидание будет ли повторять выбор задания
        """
        logging.info(f'Ожидание будет ли повторять выбор задания')
        b_working = self._question_yes_no.work()
        if b_working:
            self._next_function.set(self._wait_view_list_task)
            return
        result: bool = self._question_yes_no.result
        if result:
            self._view_list_task()  # Повторить
        else:
            raise ExceptionScriptTaskDelete('Юзер отказался повторять. Он не выбрал задание для удаления.')

    def _choice_question_delete(self):
        """
        Режим точно хотите удалить?
        """
        text = self._task_view_item[self._choice_id_task]
        self._question_yes_no = QuestionYesNo(self._connect_telebot, "", question=f"{text}\nТочно удалить?")
        self._wait_question_delete()

    def _wait_question_delete(self):
        """
        Ожидание подтверждение удаления
        """
        logging.info(f'Ожидание подтверждение удаления')
        b_working = self._question_yes_no.work()
        if b_working:
            self._next_function.set(self._wait_question_delete)
            return
        result: bool = self._question_yes_no.result
        if result:
            self._delete_task()  # Повторить
        else:
            raise ExceptionScriptTaskDelete('Юзер отказался удалять.')

    def _delete_task(self):
        """
        Команда удалить задание
        """
        TaskRule.delete_task(self._choice_id_task)
        self._connect_telebot.send_text('Команда выполнена.')
