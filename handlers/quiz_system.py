from aiogram.dispatcher import FSMContext
from connection_bot import bot, dp
from aiogram import types
import states
from keyboards import ususally, inline
from aiogram.types import ReplyKeyboardRemove
from main import add_proxy_data
from aiogram.types.input_file import InputFile
import data_base
from aiogram.dispatcher.filters import Text

QUIZ_ID = None

# --- create quiz ---
@dp.message_handler(commands=['create_quiz', 'создать_опрос'])
async def create_quiz_command(message: types.Message):
    await message.reply('Вы хотите сделать данный опрос анонимным?', reply=False,
                        reply_markup=ususally.choose_anonymity())
    await states.CreateQuizStates.is_anon.set()


@dp.message_handler(state=states.CreateQuizStates.is_anon)
async def is_anonymous_state(message: types.Message, state: FSMContext):
    if message.text == 'Нет':
        await add_proxy_data(state, {'is_anon': False})
    else:
        await add_proxy_data(state, {'is_anon': True})
    await states.CreateQuizStates.next()
    await message.reply('Введите название опроса', reply=False,
                        reply_markup=ReplyKeyboardRemove())


@dp.message_handler(state=states.CreateQuizStates.title)
async def create_quiz_title_state(message: types.Message, state: FSMContext):
    await add_proxy_data(state, {'title': message.text})
    await message.reply('Введите описание опроса, можно пропустить - /skip', reply=False)
    await states.CreateQuizStates.next()


@dp.message_handler(state=states.CreateQuizStates.description)
async def create_quiz_description_state(message: types.Message, state: FSMContext):
    photo = InputFile('handlers/example_questions.png')
    if message.text == '/skip':
        await add_proxy_data(state, {'description': None})
        await bot.send_photo(message.from_user.id, photo,
                             'Описание опроса пропущено.\nТеперь через запятую введите '
                             'вопросы для опроса. Пример на фото')
    else:
        await add_proxy_data(state, {'description': message.text})
        await bot.send_photo(message.from_user.id, photo,
                                   'Теперь через запятую введите '
                                   'вопросы для опроса. Пример на фото')
    await states.CreateQuizStates.next()


@dp.message_handler(state=states.CreateQuizStates.questions)
async def create_quiz_questions_state(message: types.Message, state: FSMContext):
    await add_proxy_data(state, {'user_id': message.from_user.id})
    questions_list = message.text.split(',')
    questions_without_spaces = list(map(str.strip, questions_list))
    clean_questions = list(filter(None, questions_without_spaces))
    # questions list without empty elements
    # await message.reply(str(clean_questions), reply=False)
    quiz = data_base.create_quiz(await state.get_data())
    for q in clean_questions:
        data_base.create_question({'question': q, 'quiz_id': quiz})
    await message.reply('Опрос успешно добавлен!', reply=False)
    await state.finish()

# --- my quiz ---


@dp.message_handler(commands=['my_quiz'])
async def my_quiz_command(message: types.Message):
    my_quiz = [*data_base.get_my_quiz(message.from_user.id)]
    if my_quiz:
        for q in my_quiz:
            current_questions = str(data_base.get_quiz_questions(q.id)).replace('[', '')\
            .replace(']', '').replace("'", '')
            description = q.description or 'Без описания'
            send_msg = await bot.send_message(message.from_user.id,
                                           f'{q.title}\n{description}\nСсылка: {q.link}\n'
                                           f'Вопросы:\n{current_questions}',
                                           parse_mode="HTML")
            send_msg_id = send_msg.message_id
            await send_msg.edit_reply_markup(reply_markup=await inline.quiz_inline_keyboard(q.id, send_msg_id))
    else:
        await bot.send_message(message.from_user.id ,'У вас нет созданных опросов!')


@dp.callback_query_handler(Text(startswith='del'))
async def delete_handler(callback: types.CallbackQuery):
    if callback.data.startswith('del_confirm_quiz'):
        data = callback.data.replace('del_confirm_quiz ', '').split(':')
        msg_id = data[0]
        quiz_id = data[1]
        await bot.edit_message_reply_markup(callback.message.chat.id,
                                            msg_id,
                                            reply_markup=inline.confirm_deletion_quiz(quiz_id ,msg_id))
    elif callback.data.startswith('del_quiz_true'):
        quiz_id = int(callback.data.replace('del_quiz_true ', ''))
        quiz_title = data_base.get_quiz(quiz_id).title
        await bot.send_message(callback.message.chat.id, f'Опрос "{quiz_title}" удален!')
        data_base.delete_quiz(quiz_id)
        await inline.delete_inline_keyboard(callback.message)
        await callback.answer()
    elif callback.data.startswith('del_quiz_false'):
        data = callback.data.replace('del_quiz_false ', '').split(':')
        msg_id = int(data[0])
        quiz_id = int(data[1])
        await bot.edit_message_reply_markup(callback.message.chat.id,
                                            msg_id,
                                            reply_markup=await inline.quiz_inline_keyboard(quiz_id, msg_id))
        await callback.answer()


# change quiz system

@dp.callback_query_handler(Text(startswith='back_to_menu'))
async def back_to_menu(callback: types.CallbackQuery):
    data = callback.data.replace('back_to_menu ', '').split(':')
    msg_id = int(data[0])
    quiz_id = int(data[1])
    await callback.message.edit_reply_markup(reply_markup=await inline.quiz_inline_keyboard(quiz_id, msg_id))


@dp.callback_query_handler(Text(startswith='change_quiz'))
async def callback_change_quiz(callback: types.CallbackQuery):
    data = callback.data.replace('change_quiz ', '').split(':')
    msg_id = int(data[0])
    quiz_id = int(data[1])
    await bot.edit_message_reply_markup(callback.message.chat.id, msg_id,
                                        reply_markup=inline.change_quiz_inline_kb(msg_id, quiz_id))


@dp.callback_query_handler(Text(startswith='choose_change'))
async def choose_change_handler(callback: types.CallbackQuery):
    global QUIZ_ID
    cb = callback.data
    data = cb.split(':')
    msg_id = int(data[0].split()[1])
    quiz_id = int(data[1])
    if cb.startswith('choose_change_anon'):
        new_state = data_base.change_quiz_anonymity(quiz_id)
        await bot.send_message(callback.message.chat.id, f'Статус опроса изменен на {new_state}')
    elif cb.startswith('choose_change_title'):
        await bot.send_message(callback.message.chat.id, 'Введите новый заголовок опроса')
        QUIZ_ID = quiz_id
        await states.ChangeQuizTitle.get_new_title.set()
    elif cb.startswith('choose_change_content'):
        await bot.send_message(callback.message.chat.id, 'Введите описание опроса.\n'
                                                         'Если не хотите его убрать, напишите слово *удалить*',
                               parse_mode='Markdown')
        QUIZ_ID = quiz_id
        await states.ChangeQuizContent.get_new_description.set()
    elif cb.startswith('choose_change_qtns'):
        data = callback.data.replace('choose_change_qtns ', '').split(':')
        quiz_id = int(data[1])
        QUIZ_ID = quiz_id
        await bot.send_message(callback.message.chat.id, 'Введите список новых вопров, по тем же правилам,'
                                                         ' как вводили при создании')
        await states.ChangeQuizQuestions.get_new_questions.set()

    await callback.answer()


@dp.message_handler(state=states.ChangeQuizTitle.get_new_title)
async def get_new_title_state(message: types.Message, state: FSMContext):
    new_title = message.text
    data_base.change_quiz_title(QUIZ_ID, new_title)
    await message.reply('Заголовок изменен!', reply=False)
    await state.finish()


@dp.message_handler(state=states.ChangeQuizContent.get_new_description)
async def get_new_title_state(message: types.Message, state: FSMContext):
    if message.text.lower() == 'удалить':
        new_description = None
    else:
        new_description = message.text
    data_base.change_quiz_content(QUIZ_ID, new_description)
    await message.reply('Заголовок изменен!', reply=False)
    await state.finish()


@dp.message_handler(state=states.ChangeQuizQuestions.get_new_questions)
async def get_new_questions(message: types.Message, state: FSMContext):
    questions_list = message.text.split(',')
    questions_without_spaces = list(map(str.strip, questions_list))
    clean_questions = list(filter(None, questions_without_spaces))
    data_base.delete_all_questions(QUIZ_ID)
    for q in clean_questions:
        data_base.create_question({'question': q, 'quiz_id': QUIZ_ID})
    await message.reply('Вопросы успешно изменены', reply=False)
    await state.finish()


