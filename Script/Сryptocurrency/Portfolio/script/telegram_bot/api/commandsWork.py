class CommandsWork:
    NONE = 'NONE'
    COMMAND_START = '/start'
    COMMAND_HELP = '/help'
    COMMAND_INPUT = '/input'
    COMMAND_OUTPUT = '/output'
    COMMAND_CONVERTATION = '/convertation'
    COMMAND_COIN_TRANSFER = '/transfer'
    COMMAND_CASH_VIEW = '/cash_view'
    COMMAND_TASK_DELETE = '/task_delete'

    @classmethod
    def get_list_operations(cls) -> list:
        list_out = [cls.COMMAND_INPUT, cls.COMMAND_OUTPUT,
                cls.COMMAND_CONVERTATION, cls.COMMAND_COIN_TRANSFER]
        for item, num in zip(list_out, range(len(list_out))):
            list_out[num] = item.replace('/', '')
        return list_out
