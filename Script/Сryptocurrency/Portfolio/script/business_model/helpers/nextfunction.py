import logging


class NextFunction:
    """
    Хранит в себе функцию, которую надо выполнить следующей, после ввода юзером ответа.
    """
    def __init__(self, cls_name: str):
        self._cls_name = cls_name
        self._next_function = None
        self._add_next_function: bool

    def set(self, fnc):
        """
        Устанавливает следующая функция для вызова, когда придет новое сообщение
        :param fnc: Следующая функция для вызова
        """
        logging.info(f'Класс {self._cls_name} следующая функция {fnc.__name__}')
        self._next_function = fnc
        self._add_next_function = True

    def work(self) -> bool:
        """
        Если было назначена следующая функция, то нужно выполнить
        :return:True - выполнилась функция
        """
        if self._next_function:
            self._add_next_function = False
            self._next_function()
            if not self._add_next_function:
                self._next_function = None
                self._add_next_function = False
            return True  # Выполнилась функция
