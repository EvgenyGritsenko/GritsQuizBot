from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from connection_bot import bot


async def delete_inline_keyboard(message):
    await bot.edit_message_reply_markup(chat_id=message.chat.id,
                                        message_id=message.message_id,
                                        reply_markup=None)


async def quiz_inline_keyboard(quiz, msg_id):
    kb = InlineKeyboardMarkup(row_width=2)
    change = InlineKeyboardButton('Изменить(в разработке)', callback_data='ok')
    delete = InlineKeyboardButton('Удалить', callback_data=f'del_confirm_quiz {msg_id}:{quiz.id}')
    results = InlineKeyboardButton('Результаты(в разработке)', callback_data='ok')
    kb.add(change, delete, results)
    return kb


def confirm_deletion_quiz(quiz_id, msg_id):
    kb = InlineKeyboardMarkup(row_width=2)
    yes = InlineKeyboardButton('Да, удалить', callback_data=f'del_quiz_true {quiz_id}')
    no = InlineKeyboardButton('Отменить удаление', callback_data=f'del_quiz_false {msg_id}:{quiz_id}')
    kb.add(yes, no)
    return kb

