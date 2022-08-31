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
        self._next_function.set(self._choice_mode)
        self._question_yes_no: QuestionYesNo
        self._choice_command: str = ""
        self._choice_id_task: int = 0
        self._task_view_item_triger: TaskViewItem = None  # сохраняет предыдущий словарь заданий, если достиг конца повторить вывод
        self._keys_task_view_item: List[int] = []  # ID записей который выведены на экран
        self._command_view: MessageType = MessageType.NONE
        self._count_view: int = 4  # сколько выводить заданий в чате
        self._MODE_ID = 'НОМЕР'
        self._MODE_LIST = 'СПИСОК'

    def work(self):
        """
        Работа класса, в зависимости от команды, опрашивает пользователя
        """
        if self._next_function.work():  # функция выполнилась
            return

    def _choice_mode(self):
        """
        Вопрос юзеру о выборе режима поиска
        """
        logging.info(f'Вопрос юзеру о выборе режима поиска')
        self._connect_telebot.view_keyboard('Выберите режим поиска:', list_view=[self._MODE_ID, self._MODE_LIST])
        self._next_function.set(self._wait_choice_mode)

    def _wait_choice_mode(self):
        """
        Ожидание ответа юзера на выбор режима поиска
        """
        logging.info(f'Ожидание ответа юзера на выбор режима поиска')
        if self._connect_telebot.message == self._MODE_ID:
            self._choice_id_task_func()
        elif self._connect_telebot.message == self._MODE_LIST:
            self._choice_type_command()
        else:
            self._choice_mode()

    def _choice_id_task_func(self):
        """
        Вопрос юзеру какой ID задания
        """
        logging.info(f'Вопрос юзеру какой ID задания')
        self._connect_telebot.send_text('Введите номер задания:')
        self._next_function.set(self._choice_id_task_func_check)

    def _choice_id_task_func_check(self):
        """
        Проверка введенного юзером  ID задания
        """
        logging.info(f'Проверка введенного юзером  ID задания')

        if not self._connect_telebot.message.isdecimal():
            self._connect_telebot.send_text(f'Не число - {self._connect_telebot.message}\n.Повторите ввод.')
            self._choice_id_task_func()

        self._choice_id_task = int(self._connect_telebot.message)
        logging.info('Выбран _choice_id_task')
        self._check_id_task()

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
            self._task_view_item_triger = None
            self._view_list_task()
        else:
            self._error_choice_type_command_check()

    def _error_choice_type_command_check(self):
        """
        Пользователь выбрал не из списка команд
        """
        self._question_yes_no = QuestionYesNo(self._connect_telebot, f"Нет в списке команды - "
                                                                     f"{self._connect_telebot.message}.")
        self._next_function.set(self._wait_answer_choice_type_command)

    def _wait_answer_choice_type_command(self):
        """
        Ожидание будет ли повторять выбор команды из списка
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
        if self._command_view == MessageType.NEXT:
            date_time_next = self._task_view_item_triger.date_next

        task_view_item: TaskViewItem = ModelTask.get_dict_completed(self._connect_telebot.id_user,
                                                                     task_type=self._choice_command,
                                                                     date_time_next=date_time_next,
                                                                     count_limit=self._count_view)

        count_task = 0
        if task_view_item.dict_task:
            count_task = len(task_view_item.dict_task)

        message_type: MessageType = MessageType.NONE
        if count_task == 0 and not self._task_view_item_triger:  # проверяет условие на 1 раз потом
            self._connect_telebot.send_text(f'Нет заданий с типом: {self._choice_command}.')
            raise ExceptionScriptTaskDelete(f'У юзера нет заданий с типом: {self._choice_command}.')
        elif not self._task_view_item_triger:  # когда показывает 1 раз
            message_type = MessageType.NEXT
            self._connect_telebot.send_text("Выберите задание из списка:")

        count = 1
        b_end_task: bool = False
        for key, item in task_view_item.dict_task.items():
            self._keys_task_view_item.append(key)
            if count == count_task:
                if count < self._count_view:
                    b_end_task = True
                    message_type = MessageType.VALUE
                self._connect_telebot.view_keyboard_task(text_keyboard=item,
                                                         text_key=str(key),
                                                         type_message=message_type)
            else:
                self._connect_telebot.view_keyboard_task(text_keyboard=item,
                                                         text_key=str(key),
                                                         type_message=MessageType.VALUE)
            count += 1

        if count_task == 0 or b_end_task:
            self._connect_telebot.send_text(text_send=f"Задания закончились.\n"
                                                      f"Выберите задание из списка выше.")


        self._task_view_item_triger = task_view_item.__copy__()

        self._next_function.set(self._view_list_task_check)

    def _view_list_task_check(self):
        """
        Режим проверяет ответ пользователя, по выбранному заданию из списка
        """
        logging.info(f'Режим проверить "{self._connect_telebot.message}" - это ID задания?')
        if self._connect_telebot.message == NameKey.NEXT.value:  # юзер нажал на следующее
            self._command_view = MessageType.NEXT
            self._view_list_task()
            self._next_function.set(self._view_list_task_check)
            return

        if not self._connect_telebot.message.isdecimal():
            self._error_view_list_task()

        if int(self._connect_telebot.message) in self._keys_task_view_item:
            self._choice_id_task = int(self._connect_telebot.message)
            logging.info('Выбран _choice_id_task')
            self._check_id_task()
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

    def _check_id_task(self):
        """
        Проверить есть ли у выбранного задания зависимости
        :return:
        """
        dict_task: Dict[int, str] = ModelTask.get_dict_task_subject(self._choice_id_task)
        if not dict_task:
            self._choice_question_delete()

        self._connect_telebot.send_text(text_send=f'УДАЛИТЬ НЕВОЗМОЖНО!\n'
                                                  f'Имеются зависимые задания.')
        for item in dict_task.values():
            self._connect_telebot.send_text(text_send=item.__str__())
        raise ExceptionScriptTaskDelete('УДАЛИТЬ НЕВОЗМОЖНО! Имеются зависимые задания.')

    def _choice_question_delete(self):
        """
        Режим точно хотите удалить?
        """
        task_view_item: TaskViewItem = ModelTask.get_dict_completed(self._connect_telebot.id_user,
                                                                    task_type=self._choice_command,
                                                                    id_task=self._choice_id_task)
        text = task_view_item.dict_task[self._choice_id_task]
        self._connect_telebot.send_text(text_send=f'Будет удалено:\n{text}')
        self._question_yes_no = QuestionYesNo(self._connect_telebot, "", question="Точно удалить?")
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
