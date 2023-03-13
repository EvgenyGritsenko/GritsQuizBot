from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def choose_anonymity():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    yes = KeyboardButton('Да')
    no = KeyboardButton('Нет')
    kb.add(yes, no)
    return kb


def start_passing_agree_or_not():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    yes = KeyboardButton('Начать')
    no = KeyboardButton('Нет, начну позже')
    kb.add(yes, no)
    return kb


def start_passing_quiz():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    start = KeyboardButton('Начать')
    cancel = KeyboardButton('Отмена')
    kb.add(start, cancel)
    return kb


