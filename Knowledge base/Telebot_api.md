
[https://qna.habr.com/q/858533](Расположение кнопок в чате)    
start_markup = telebot.types.InlineKeyboardMarkup()

# первый ряд (две кнопки)
btn1= telebot.types.InlineKeyboardButton('действие 1', callback_data='1')
btn2= telebot.types.InlineKeyboardButton('действие 2', callback_data='2')
start_markup.row(btn1, btn2)

