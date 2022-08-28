import logging
from datetime import datetime
from telegram_bot.api.telegramApi import ConnectTelebot
from business_model.helpers.nextfunction import NextFunction
from business_model.helpers.questionYesNo import QuestionYesNo

class ExceptionChoiceDate(Exception):
    def __init__(self, err_message: str = ''):
        logging.error(f'Класс {ExceptionChoiceDate.__name__} - {err_message}')
        super().__init__(err_message)


class ChoiceDate:
    """
    Конвертация даты и времени
    """

    def __init__(self, connect_telebot: ConnectTelebot):
        self._connect_telebot = connect_telebot
        self._next_function = NextFunction(ChoiceDate.__name__)
        self._next_function.set(self._input_date_time_question)   # первое что выполнит скрипт
        self._result: datetime = None
        self._question_yes_no: QuestionYesNo

    @classmethod
    def convert(cls, date_time_str: str) -> datetime:
        date_time = cls._variant_5(date_time_str)
        if date_time:
            return date_time

        date_time = cls._variant_3(date_time_str)
        if date_time:
            return date_time

        date_time = cls._variant_4(date_time_str)
        if date_time:
            return date_time

        date_time_str = cls._replace_symbol(date_time_str)
        date_time = cls._variant_1(date_time_str)
        if date_time:
            return date_time
        date_time = cls._variant_2(date_time_str)
        if date_time:
            return date_time

        if not date_time:
            raise ExceptionChoiceDate(f'cls:{cls.__name__} Ошибка конвертации даты и времени')

    @classmethod
    def _variant_1(cls, date_time_str: str) -> datetime:
        """
        Конвертация используя шаблон
        :param date_time_str: Дата строковая
        :return: Новая дата
        """
        try:
            template: str = '%d.%m.%y %H.%M.%S'
            return datetime.strptime(date_time_str, template)
        except Exception:
            logging.info(f'cls:{cls.__name__} def:{cls._variant_1.__name__} Ошибка конвертации по шаблону "{template}"')

    @classmethod
    def _variant_2(cls, date_time_str: str) -> datetime:
        """
       Конвертация используя шаблон
       :param date_time_str: Дата и время строковая
       :return: Новая дата и время
       """
        try:
            template: str = '%d.%m.%Y %H.%M.%S'
            return datetime.strptime(date_time_str, template)
        except Exception:
            logging.info(f'cls:{cls.__name__} def:{cls._variant_2.__name__} Ошибка конвертации по шаблону "{template}"')

    @classmethod
    def _variant_3(cls, date_time_str: str) -> datetime:
        """
       Конвертация используя шаблон
       :param date_time_str: Дата и время строковая
       :return: Новая дата и время
       """
        try:
            template: str = '%d.%m.%Y, %H:%M:%S'
            return datetime.strptime(date_time_str, template)
        except Exception:
            logging.info(f'cls:{cls.__name__} def:{cls._variant_3.__name__} Ошибка конвертации по шаблону "{template}"')

    @classmethod
    def _variant_4(cls, date_time_str: str) -> datetime:
        """
       Конвертация используя шаблон
       :param date_time_str: Дата и время строковая
       :return: Новая дата и время
       """
        try:
            template: str = '%Y-%m-%d %H:%M:%S'
            return datetime.strptime(date_time_str, template)
        except Exception:
            logging.info(f'cls:{cls.__name__} def:{cls._variant_4.__name__} Ошибка конвертации по шаблону "{template}"')

    @classmethod
    def _variant_5(cls, date_time_str: str) -> datetime:
        """
       Конвертация используя шаблон
       :param date_time_str: Дата и время строковая
       :return: Новая дата и время
       """
        try:
            template: str = '%Y-%m-%d %H:%M:%S.%f'
            return datetime.strptime(date_time_str, template)
        except Exception:
            logging.info(f'cls:{cls.__name__} def:{cls._variant_5.__name__} Ошибка конвертации по шаблону "{template}"')

    @classmethod
    def _replace_symbol(cls, date_time_str: str) -> str:
        """
        Заменяет символы
        :param date_time_str: Изменить строку
        :return: Новая строка
        """
        date_time_str = date_time_str.replace(",", ".")
        date_time_str = date_time_str.replace("/", ".")
        date_time_str = date_time_str.replace("/", ".")
        date_time_str = date_time_str.replace(":", ".")
        date_time_str = date_time_str.replace("-", ".")
        return date_time_str

    def _input_date_time_question(self):
        """
        Режим вопрос пользователю введите дату и время перевода
        """
        if self._connect_telebot.debug:
            self._connect_telebot.view_keyboard('Введите дату и время:', list_view=['04.05.2022 10.10.10'])
        else:
            self._connect_telebot.send_text('Введите дату и время:')
        self._next_function.set(self._input_date_time_answer)

    def _input_date_time_answer(self):
        """
        Режим проверки даты и времени
        """
        try:
            self._result = ChoiceDate.convert(self._connect_telebot.message)
            logging.info(f'Преобразована дата - {self._result}')
        except Exception as err:
            logging.info(f'Невозможно преобразовать дату и время - "{self._connect_telebot.message}"')
            self._question_yes_no = QuestionYesNo(self._connect_telebot, "Ошибка преобразования даты")
            self._wait_answer_repeat()

    def _wait_answer_repeat(self):
        b_working = self._question_yes_no.work()
        if b_working:
            self._next_function.set(self._wait_answer_repeat)
            return
        result: bool = self._question_yes_no.result
        if result:
            self._input_date_time_question()
        else:
            raise ExceptionChoiceDate('Пользователь отказался повторять ввод даты еще раз.')

    @property
    def result(self):
        return self._result

    def work(self) -> bool:
        self._next_function.work()
        if not self._result:
            return True

    @classmethod
    def convert_to_str(cls, date_time_str: str) -> str:
        date_time = cls.convert(date_time_str)
        return date_time.strftime("%d.%m.%Y, %H:%M:%S")











