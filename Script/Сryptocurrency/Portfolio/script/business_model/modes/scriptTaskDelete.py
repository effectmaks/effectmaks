import logging


from base.models.task import ModelTask
from business_model.helpers.nextfunction import NextFunction
from business_model.helpers.questionYesNo import QuestionYesNo
from business_model.taskrule import TaskRule
from telegram_bot.api.commandsWork import CommandsWork
from telegram_bot.api.telegramApi import ConnectTelebot, MessageType


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
        self._task_dict = ModelTask.get_dict_completed(self._connect_telebot.id_user,
                                                       task_type=self._choice_command)
        if not self._task_dict:
            self._connect_telebot.send_text(f'Нет заданий с типом: {self._choice_command}.')
            raise ExceptionScriptTaskDelete(f'У юзера нет заданий с типом: {self._choice_command}.')
        self._connect_telebot.view_keyboard('Выберите задание:', dict_view=self._task_dict,
                                            type_message=MessageType.KEY)
        self._next_function.set(self._view_list_task_check)

    def _view_list_task_check(self):
        """
        Режим  проверяет ответ пользователя, по выбранному заданию
        """
        logging.info(f'Режим проверить "{self._connect_telebot.message}" - это ID задания?')
        if not self._connect_telebot.message.isdecimal():
            self._error_view_list_task()

        if int(self._connect_telebot.message) in self._task_dict.keys():
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
        text = self._task_dict[self._choice_id_task]
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
