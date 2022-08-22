import logging
from typing import Dict, List
from enum import Enum
from decimal import Decimal
from datetime import datetime

from base.models.cash import ModelCash, CashItem
from business_model.helpers.nextfunction import NextFunction
from business_model.helpers.questionYesNo import QuestionYesNo
from telegram_bot.api.telegramApi import ConnectTelebot, MessageType


class ChoiceCashResult:
    def __init__(self):
        self.amount: Decimal = Decimal(0)
        self.id_cash: int = 0
        self.coin: str = ""
        self.price_buy: Decimal = Decimal(0)
        self.coin_avr: str = ""

    def __bool__(self) -> bool:
        if self.id_cash != 0 and self.coin != "":
            return True
        return False


class ModesChoiceCash(Enum):
    ONE = 'ONE'
    LIST = 'LIST'


class ExceptionChoiceCash(Exception):
    def __init__(self, err_message: str = ''):
        logging.error(f'Класс {ExceptionChoiceCash.__name__} - {err_message}')
        super().__init__(err_message)


class ChoiceCash:
    def __init__(self, connect_telebot: ConnectTelebot,
                 id_safe_user: int,
                 message: str,
                 filter_coin_view_no: str = '',
                 filter_coin_view: str = '',
                 filter_cash_date_before: datetime = None):
        logging.info(f'Создание объекта {ChoiceCash.__name__}')
        self._connect_telebot = connect_telebot
        self._mode_work = ModesChoiceCash.ONE
        self._message_str: str = message
        self._next_function = NextFunction(ChoiceCash.__name__)
        self._dict_cash: Dict
        self._list_result: List[ChoiceCashResult] = []  # хранит результат выбора пользователя
        self._id_safe_user = id_safe_user
        self._filter_coin_view_no = filter_coin_view_no  # не показывать монету в сейфе
        self._filter_coin_view = filter_coin_view  # показывать только эту монету в сейфе
        self._filter_cash_date_before = filter_cash_date_before  # показывать только до этой даты
        self._set_next_function()
        self._work: bool = True  # Когда все сделано закончить работу. Сейчас выбор cash в работе
        self._amount_sell = Decimal(0)
        self._amount_sell_left = Decimal(0)
        self._list_cash_no_view: List[int] = []

    def _set_next_function(self):
        """
        Выбор следующей функции в зависимости от режима
        :return:
        """
        if self._mode_work == ModesChoiceCash.ONE:
            self._next_function.set(self._question_choice_cash)  # первое что выполнит скрипт
        if self._mode_work == ModesChoiceCash.LIST:
            self._next_function.set(self._check_last_cash)  # первое что выполнит скрипт

    def _question_choice_cash(self):
        """
        Режим показать счета у сейфа
        """
        logging.info('Режим показать счета у сейфа')
        self._dict_cash: Dict[int, CashItem] = ModelCash.dict_amount(id_safe_user=self._id_safe_user,
                                                                     filter_coin_view_no=self._filter_coin_view_no,
                                                                     filter_coin_view=self._filter_coin_view,
                                                                     list_cash_no_view=self._list_cash_no_view,
                                                                     filter_cash_date_before=self._filter_cash_date_before)
        if not self._dict_cash:
            self._connect_telebot.send_text('В сейфе нет счетов для продажи.')
            raise ExceptionChoiceCash('В сейфе нет счетов для продажи.')
        dict_view: Dict = {id: self._key_value(item) for id, item in
                           self._dict_cash.items()}
        self._connect_telebot.view_keyboard(self._message_str, dict_view=dict_view, type_message=MessageType.KEY)
        self._next_function.set(self._answer_choice_cash)

    def _key_value(self, item: CashItem) -> str:
        price_avr: str = f'({item.coin_avr} {item.price_buy})'
        if price_avr in ["(None 0.0)", "( 0.0)", "( None)"]:
            price_avr = '(-)'
        return f'{item.date_time[:16]}   {item.coin}: {item.amount} {price_avr}'

    def _answer_choice_cash(self):
        """
        Проверка пользователя, какой счет он выбрал.
        """
        logging.info("Проверка пользователя, какой счет он выбрал.")
        try:
            cash_key = int(self._connect_telebot.message)
            if cash_key in self._dict_cash.keys():
                logging.info(f'Выбран id_cash: {cash_key}')
                result = ChoiceCashResult()
                result.id_cash = cash_key
                result.amount = self._dict_cash.get(cash_key).amount
                result.coin = self._dict_cash.get(cash_key).coin
                result.price_buy = self._dict_cash.get(cash_key).price_buy
                result.coin_avr = self._dict_cash.get(cash_key).coin_avr
                self._result_list_join(result)
                self._list_cash_no_view.append(result.id_cash)
                if self._mode_work == ModesChoiceCash.LIST:
                    self._check_last_cash()  # Проверка достаточно счетов?
                elif self._mode_work == ModesChoiceCash.ONE:
                    self._work = False  # Выбрали одну ячейку и закончить работу
            else:
                self._err_answer_choice_cash()
        except Exception as err:
            logging.info(f'Ошибка проверки счета. Сообщение - {self._connect_telebot.message}. ERR: {err}')
            self._err_answer_choice_cash()

    def _err_answer_choice_cash(self):
        self._question_yes_no = QuestionYesNo(self._connect_telebot,
                                              f'"{self._connect_telebot.message}" - счета нет в списке.')
        self._wait_answer_repeat_id_cash()

    def _wait_answer_repeat_id_cash(self):
        b_working = self._question_yes_no.work()
        if b_working:
            self._next_function.set(self._wait_answer_repeat_id_cash)
            return
        result: bool = self._question_yes_no.result
        if result:
            self._question_choice_cash()  # Повторить
        else:
            raise ExceptionChoiceCash('Юзер отказался выбирать счет.')

    def _result_list_join(self, item: ChoiceCashResult):
        """
        Добавляет в результат работы ячейку листа.
        :param item: Ячейка для добавления
        """
        logging.info(f'Добавить в результат ID счет: {item.id_cash}')
        self._list_result.append(item)

    def _calc_amount_sell_left(self) -> Decimal:
        """
        Высчитывает сколько осталось объема для перевода в зависимости от выбранных счетов
        :return:
        """
        amount_sell_sum = Decimal(0)
        for item in self._list_result:
            amount_sell_sum += item.amount
        return self._amount_sell - amount_sell_sum

    def _check_last_cash(self):
        """
        Проверка достаточно выбрано счетов чтобы заполнить объем продажи self._amount_sell.
        Если НЕТ команда на добавить
        :return:
        """
        logging.info('Проверить достаточно выбрано счетов.')
        result_left = self._calc_amount_sell_left()
        if result_left > 0:
            logging.info(f'Требуется {self._amount_sell} осталось {result_left}.')
            self._message_str = f'Требуется {self._amount_sell} осталось {result_left}.\n' \
                                f'Выберите счет снятия:'
            self._question_choice_cash()
            return
        logging.info('Счетов достаточно')
        self._amount_cash_last_edit(result_left)
        self._work = False

    def _amount_cash_last_edit(self, amount_minus: Decimal):
        """
        Изменяет объем продажи последней выбранной ячейки
        """
        logging.info('Изменить объем продажи последней ячейки')
        count = len(self._list_result)
        self._list_result[count-1].amount += amount_minus

    @property
    def result_first_item(self) -> ChoiceCashResult:
        """
        В режиме запроса на один счет ModesChoiceCash.ONE
        :return: ChoiceCashResult инфо счета
        """
        if self._list_result:
            return self._list_result[0]
        else:
            raise ExceptionChoiceCash('Запрос на результат. Массив пустой.')

    @property
    def list_result(self) -> List[ChoiceCashResult]:
        """
        В режиме запроса на лист из счетов ModesChoiceCash.LIST
        :return: Лист с ChoiceCashResult инфо счета
        """
        if self._list_result:
            return self._list_result

    @property
    def amount_sell(self) -> Decimal:
        return self._amount_sell

    @amount_sell.setter
    def amount_sell(self, amount_sell: Decimal):
        self._amount_sell = amount_sell

    def work(self) -> bool:
        """
        Проверка режим выбора cash в работе
        :return:
        """
        self._next_function.work()
        return self._work

    def set_type_amount_list(self, amount_sell: Decimal):
        """
        Установить режим поиска дополнительных счетов
        amount_sell: Decimal Объем который надо продать или вывести
        :return:
        """
        logging.info('Установка режима ModesChoiceCash.LIST')
        self._work = True
        self._mode_work = ModesChoiceCash.LIST
        self._amount_sell = amount_sell
        self._set_next_function()



