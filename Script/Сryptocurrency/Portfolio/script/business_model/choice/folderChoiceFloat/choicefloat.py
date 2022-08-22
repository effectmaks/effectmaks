import logging
from decimal import Decimal
from enum import Enum

from business_model.choice.folderChoiceFloat.questionAmount import QuestionAmount, TypesAnswerAmount
from business_model.helpers.nextfunction import NextFunction
from business_model.helpers.questionYesNo import QuestionYesNo
from telegram_bot.api.telegramApi import ConnectTelebot


class ExceptionChoiceFloat(Exception):
    def __init__(self, err_message: str = ''):
        logging.error(f'Класс {ExceptionChoiceFloat.__name__} - {err_message}')
        super().__init__(err_message)


class TypesChoiceFloat(Enum):
    AMOUNT = 'AMOUNT'  # только ввод объема
    CASH = 'CASH'  # ввод объема, и выбор режима выбрать дополнительные счета


class ChoiceFloat:
    def __init__(self, connect_telebot: ConnectTelebot,
                 question_main: str,
                 max_number: Decimal = 0,
                 type_work: TypesChoiceFloat = TypesChoiceFloat.AMOUNT):
        self._connect_telebot = connect_telebot
        self._question_main = question_main
        self._max_number = max_number
        self._type_work = type_work
        self._next_function = NextFunction(ChoiceFloat.__name__)
        self._next_function.set(self._input_float_question)  # первое что выполнит скрипт
        self._question_amount: QuestionAmount
        self._result_float: Decimal = None
        self._zero = False
        self._question_yes_no: QuestionYesNo
        self._work = True
        self._choice_type_amount: TypesAnswerAmount = None

    def _input_float_question(self):
        """
        Режим вопроса
        """
        logging.info(f'Режим вопроса - {self._question_main}')
        self._connect_telebot.send_text(self._question_main)
        self._next_function.set(self._input_float_answer)

    def _input_float_answer(self):
        """
        Режим проверка ответа
        :return:
        """
        logging.info(f'Режим проверки ответа на - {self._question_main}')
        message: str = self._connect_telebot.message
        result_float = self._isfloat(message)
        if message == '0':
            self._zero = True
        if result_float or self._zero:
            if self._check_min_max(result_float):
                self._work_end(result_float)
            else:
                if self._type_work == TypesChoiceFloat.AMOUNT:
                    self._question_extra(f'Число должно быть от 0 до {self._max_number}. Повторить ввод?')
                else:
                    self._result_float = result_float
                    self._set_question_amount()
        else:
            logging.info('Невозможно преобразовать число.')
            self._question_extra("Ошибка преобразования числа. Повторить ввод?")

    def _work_end(self, result_float: Decimal):
        self._result_float = result_float
        logging.info(f'Выбрано число - {self._result_float}')
        self._work = False

    def _set_question_amount(self):
        logging.info(f'Число должно быть от 0 до {self._max_number}.')
        self._question_amount = QuestionAmount(self._connect_telebot,
                                               text_err=f'Введенный объем {self._result_float}, '
                                                        f'превышает объем {self._max_number} счета.')
        self._wait_question_amount()

    def _wait_question_amount(self):
        b_working = self._question_amount.work()
        if b_working:
            self._next_function.set(self._wait_question_amount)
            return
        result = self._question_amount.result
        if result == TypesAnswerAmount.REPEAT_AMOUNT:
            # Введенный ранее объем превышал self._max_number, поэтому заново спросить объем
            self._input_float_question()
        elif result == TypesAnswerAmount.CHOICE_CASH:
            self._set_question_repeat(result)
        elif result == TypesAnswerAmount.CANCEL:
            raise ExceptionChoiceFloat(f'Пользователь решил остановить работу режима')
        else:
            raise ExceptionChoiceFloat(f'Пользователь не выбрал пункт из списка AMOUNT')

    def _set_question_repeat(self, result: TypesAnswerAmount):
        """
        Вопрос подтвердить введенный объем ранее
        Пользователь выбрал режим TypesAnswerAmount.CHOICE_CASH
        :param result: TypesAnswerAmount Выбранный режим
        """
        self._choice_type_amount = result
        self._question_extra(f'Объем будет равняться {self._result_float}?')  # повторить ввод объема

    def _question_extra(self, message_err: str):
        """
        Задать дополнительный вопрос пользователю да/нет
        :param message_err: Вопрос
        """
        self._question_yes_no = QuestionYesNo(self._connect_telebot, message_err, question='')
        self._wait_answer_repeat()

    def _check_min_max(self, result: Decimal) -> bool:
        if not self._max_number:
            return True
        elif result > self._max_number and self._choice_type_amount == TypesAnswerAmount.CHOICE_CASH:
            return True
        elif result <= self._max_number and self._choice_type_amount == TypesAnswerAmount.CHOICE_CASH:
            self._connect_telebot.send_text(f'Число должно быть больше {self._max_number}')
        elif 0 <= result <= self._max_number:
            return True

    def _wait_answer_repeat(self):
        """
        Ожидает ответ пользователя
        :return:
        """
        logging.info('Режим ответ на вопрос ДА/НЕТ')
        b_working = self._question_yes_no.work()
        if b_working:
            self._next_function.set(self._wait_answer_repeat)
            return
        result: bool = self._question_yes_no.result
        if result and self._choice_type_amount == TypesAnswerAmount.CHOICE_CASH:
            self._work_end(self._result_float)  # Юзер подтвердил что число верное CHOICE_CASH
        elif not result and self._choice_type_amount == TypesAnswerAmount.CHOICE_CASH:
            self._input_float_question()  # повторить ввод юзер хочет поменять число CHOICE_CASH
        elif result:
            # повторить ввод не получилось преобразовать число, или оно больше заданного в режиме Amount
            self._input_float_question()
        else:
            raise ExceptionChoiceFloat(f'Юзер отказался вводить объем - {self._connect_telebot.message}')

    def _isfloat(self, value_str: str) -> Decimal:
        try:
            value_str = value_str.replace(',', '.')
            return Decimal(value_str)
        except Exception:
            pass

    @property
    def result(self) -> Decimal:
        return self._result_float

    @property
    def choice_type_amount(self) -> TypesAnswerAmount:
        return self._choice_type_amount

    def work(self) -> bool:
        self._next_function.work()
        if self._zero:
            return False
        return self._work
