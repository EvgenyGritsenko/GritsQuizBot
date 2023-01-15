from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def choose_anonymity():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    yes = KeyboardButton('Да')
    no = KeyboardButton('Нет')
    kb.add(yes, no)
    return kb

