import logging
from datetime import datetime
from decimal import Decimal
from typing import List

from base.models.cash import ModelCash
from base.models.cashsell import ModelCashSell
from base.models.eventbank import ModelEventBank
from base.models.task import ModelTask, TaskStatus
from business_model.choice.choicedate import ChoiceDate
from business_model.choice.choicepriceavr import TypeConvertatuion
from business_model.choice.choicecash import ChoiceCashResult
from telegram_bot.api.commandsWork import CommandsWork, TypeWork


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
        self.safe_buy_name: str = ''
        self.safe_sell_name: str = ''
        self.id_cash: int = 0
        self.coin: str = ""
        self.amount: Decimal = None
        self.amount_sell: Decimal = Decimal(0)
        self.price_avr: Decimal = None
        self.type_convertation: TypeConvertatuion = TypeConvertatuion.NONE
        self.fee: Decimal = None
        self.coin_avr: str = ""
        self._id_task: int = 0
        self.list_cash: List[ChoiceCashResult] = []
        self.comment: str = ""

    def run(self):
        logging.info(f'Команда выполнить задание. Тип: {self._command_type}')
        if self._command_type == TypeWork.TYPE_INPUT:
            self._run_command_bank_input()
        elif self._command_type == TypeWork.TYPE_OUTPUT:
            self._run_command_bank_output()
        elif self._command_type == TypeWork.TYPE_CONVERTATION:
            self._run_command_bank_convertation()
        elif self._command_type == TypeWork.TYPE_COIN_TRANSFER:
            self._run_command_bank_coin_transfer()

    def _run_command_bank_input(self):
        try:
            desc = ModelTask.desc_in_or_out('+', self.safe_buy_name, self.coin, self.amount, self.fee)
            self._id_task = ModelTask.create(id_user=self._id_user, task_type=self._command_type, desc=desc,
                                             status=TaskStatus.RUN, date_time=self.date_time)
            id_cash_buy = ModelCash.add(id_safe_user=self.id_safe_user, date_time=self.date_time, coin=self.coin,
                                        amount_buy=self.amount, id_task=self._id_task)
            ModelEventBank.add(id_task=self._id_task, type=self._command_type, date_time=self.date_time,
                               id_cash_buy=id_cash_buy, fee=self.fee, comment=self.comment)
            ModelTask.set_completed_status(self._id_task)
            logging.info(f'Задание {CommandsWork.COMMAND_INPUT} выполнено')
        except Exception as err:
            logging.error(f'Задание {CommandsWork.COMMAND_INPUT} НЕ выполнено')
            self._task_delete(id_task_delete=self._id_task)
            raise ExceptionTaskList(f'Ошибка {CommandsWork.COMMAND_INPUT}: {err}')

    def _run_command_bank_output(self):
        try:
            desc = ModelTask.desc_in_or_out('-', self.safe_sell_name, self.list_cash[0].coin, self.amount, self.fee)
            self._id_task = ModelTask.create(id_user=self._id_user, task_type=self._command_type, desc=desc,
                                             status=TaskStatus.RUN, date_time=self.date_time)
            list_cash_sell: List[int] = []
            for item in self.list_cash:
                id_cash = ModelCashSell.add(date_time=self.date_time, id_cash=item.id_cash,
                                            amount_sell=item.amount, id_task=self._id_task)
                list_cash_sell.append(id_cash)

            for id_cash_sell in list_cash_sell:
                ModelEventBank.add(id_task=self._id_task, type=self._command_type, date_time=self.date_time,
                                   id_cash_sell=id_cash_sell, fee=self.fee,
                                   comment=self.comment)

            ModelTask.set_completed_status(self._id_task)
            logging.info(f'Задание {CommandsWork.COMMAND_OUTPUT} выполнено')
        except Exception as err:
            logging.error(f'Задание {CommandsWork.COMMAND_OUTPUT} НЕ выполнено')
            self._task_delete(id_task_delete=self._id_task)
            raise ExceptionTaskList(f'Ошибка {CommandsWork.COMMAND_OUTPUT}: {err}')

    def _run_command_bank_convertation(self):
        try:
            desc = ModelTask.desc_convertation_transfer(coin_sell=self.list_cash[0].coin, amount_sell=self.amount_sell,
                                                    coin_buy=self.coin, amount_buy=self.amount,
                                                    safe_sell=self.safe_buy_name, safe_buy=self.safe_buy_name)
            self._id_task = ModelTask.create(id_user=self._id_user, task_type=self._command_type, desc=desc,
                                             status=TaskStatus.RUN, date_time=self.date_time)
            list_cash_sell: List[int] = []
            for item in self.list_cash:
                id_cash = ModelCashSell.add(date_time=self.date_time, id_cash=item.id_cash,
                                            amount_sell=item.amount, id_task=self._id_task,
                                            price_sell=self._get_price_sell())
                list_cash_sell.append(id_cash)
            id_cash_buy = ModelCash.add(id_safe_user=self.id_safe_user, date_time=self.date_time, coin=self.coin,
                                        amount_buy=self.amount, price_buy=self._get_price_buy(), id_task=self._id_task,
                                        coin_avr=self.coin_avr)
            for id_cash_sell in list_cash_sell:
                ModelEventBank.add(id_task=self._id_task, type=self._command_type, date_time=self.date_time,
                                   id_cash_buy=id_cash_buy, id_cash_sell=id_cash_sell, fee=self.fee,
                                   comment=self.comment)
            ModelTask.set_completed_status(self._id_task)
            logging.info(f'Задание {CommandsWork.COMMAND_CONVERTATION} выполнено')
        except Exception as err:
            logging.error(f'Задание {CommandsWork.COMMAND_CONVERTATION} НЕ выполнено')
            self._task_delete(id_task_delete=self._id_task)
            raise ExceptionTaskList(f'Ошибка {CommandsWork.COMMAND_CONVERTATION}: {err}')

    def _run_command_bank_coin_transfer(self):
        try:
            desc = ModelTask.desc_convertation_transfer(coin_sell=self.list_cash[0].coin, amount_sell=self.amount_sell,
                                                        coin_buy=self.coin, amount_buy=self.amount,
                                                        safe_sell=self.safe_sell_name, safe_buy=self.safe_buy_name,
                                                        fee=self.fee)
            self._id_task = ModelTask.create(id_user=self._id_user, task_type=self._command_type, desc=desc,
                                             status=TaskStatus.RUN, date_time=self.date_time)
            list_cash_sell: List[int] = []
            for item in self.list_cash:
                id_cash = ModelCashSell.add(date_time=self.date_time, id_cash=item.id_cash,
                                            amount_sell=item.amount, id_task=self._id_task, price_sell=Decimal(0))
                list_cash_sell.append(id_cash)
            coin_buy = self.list_cash[0].coin  # в любом случае монеты будут одинаковы, и 0 ячейка будет занята
            id_cash_buy = ModelCash.add(id_safe_user=self.id_safe_user, date_time=self.date_time,
                                        coin=coin_buy,
                                        amount_buy=self.amount, price_buy=self.price_avr, id_task=self._id_task,
                                        coin_avr=self.coin_avr)
            for id_cash_sell in list_cash_sell:
                ModelEventBank.add(id_task=self._id_task, type=self._command_type, date_time=self.date_time,
                                   id_cash_buy=id_cash_buy, id_cash_sell=id_cash_sell, fee=self.fee,
                                   comment=self.comment)
            ModelTask.set_completed_status(self._id_task)
            logging.info(f'Задание {CommandsWork.COMMAND_COIN_TRANSFER} выполнено')
        except Exception as err:
            logging.error(f'Задание {CommandsWork.COMMAND_COIN_TRANSFER} НЕ выполнено')
            if self._id_task != 0:
                self._task_delete(id_task_delete=self._id_task)
            raise ExceptionTaskList(f'Ошибка {CommandsWork.COMMAND_COIN_TRANSFER}: {err}')

    def _get_price_sell(self) -> Decimal:
        if self.type_convertation == TypeConvertatuion.SELL:
            return self.price_avr
        else:
            return Decimal(0)

    def _get_price_buy(self) -> Decimal:
        if self.type_convertation == TypeConvertatuion.BUY:
            return self.price_avr
        else:
            return Decimal(0)

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
            ModelCashSell.delete_task_run(id_task=id_task_delete)
            ModelCash.delete_task_run(id_task=id_task_delete)
            ModelEventBank.delete_task_run(id_task=id_task_delete)
            ModelTask.set_delete_status(id_task_delete)
            logging.info(f'ID задание:{id_task_delete} успешно удалено.')
        except Exception as err:
            logging.error(f'Не удалось удалить все записи с ID_task: {id_task_delete} -  {str(err)}')

    @classmethod
    def delete_task(cls, id_task_delete: int = 0):
        """
        Команда юзера удалить задание
        :param id_task_delete:
        :return:
        """
        logging.info(f'Команда юзера - Удалить задание ID:{id_task_delete}')
        ModelTask.set_run_status(id_task_delete)
        cls._task_delete(id_task_delete)
