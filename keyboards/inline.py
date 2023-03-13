from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from connection_bot import bot


async def help_inline_keyboard():
    kb = InlineKeyboardMarkup(row_width=1)
    answer_questions = InlineKeyboardButton('Как мне пройти опрос?',
                                            callback_data='help_answer_questions')
    create_quiz = InlineKeyboardButton('Как мне создать опрос?',
                                       callback_data='help_create_quiz')
    my_quiz = InlineKeyboardButton('Как мне получить ответы, удалить мой опрос?',
                                   callback_data='help_my_quiz')
    kb.add(answer_questions, create_quiz, my_quiz)
    return kb


async def delete_inline_keyboard(message):
    await bot.edit_message_reply_markup(chat_id=message.chat.id,
                                        message_id=message.message_id,
                                        reply_markup=None)


async def quiz_inline_keyboard(quiz_id, msg_id):
    kb = InlineKeyboardMarkup(row_width=2)
    change = InlineKeyboardButton('Редактировать', callback_data=f'change_quiz {msg_id}:{quiz_id}')
    delete = InlineKeyboardButton('Удалить', callback_data=f'del_confirm_quiz {msg_id}:{quiz_id}')
    results = InlineKeyboardButton('Результаты', callback_data=f'results:{quiz_id}')
    kb.add(change, delete, results)
    return kb


def confirm_deletion_quiz(quiz_id, msg_id):
    kb = InlineKeyboardMarkup(row_width=2)
    yes = InlineKeyboardButton('Да, удалить', callback_data=f'del_quiz_true {quiz_id}')
    no = InlineKeyboardButton('Отменить удаление', callback_data=f'del_quiz_false {msg_id}:{quiz_id}')
    kb.add(yes, no)
    return kb


def change_quiz_inline_kb(msg_id, quiz_id):
    kb = InlineKeyboardMarkup(row_width=2)
    anon = InlineKeyboardButton('Анонимность', callback_data=f'choose_change_anon {msg_id}:{quiz_id}')
    title = InlineKeyboardButton('Заголовок', callback_data=f'choose_change_title {msg_id}:{quiz_id}')
    content = InlineKeyboardButton('Описание', callback_data=f'choose_change_content {msg_id}:{quiz_id}')
    questions = InlineKeyboardButton('Вопросы', callback_data=f'choose_change_qtns {msg_id}:{quiz_id}')
    back = InlineKeyboardButton('←Назад', callback_data=f'back_to_menu {msg_id}:{quiz_id}')
    kb.add(anon, title, content, questions, back)
    return kb



