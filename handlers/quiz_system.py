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
    my_quiz = data_base.get_my_quiz(message.from_user.id)
    for q in my_quiz:
        current_questions = str(data_base.get_quiz_questions(q.id)).replace('[', '')\
        .replace(']', '').replace("'", '')
        description = q.description or 'Без описания'
        send_msg = await bot.send_message(message.from_user.id,
                                       f'{q.title}\n{description}\nСсылка: {q.link}\n'
                                       f'Вопросы:\n{current_questions}',
                                       parse_mode="HTML")
        send_msg_id = send_msg.message_id
        await send_msg.edit_reply_markup(reply_markup=await inline.quiz_inline_keyboard(q, send_msg_id))


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
        quiz = data_base.get_quiz(quiz_id)
        await bot.edit_message_reply_markup(callback.message.chat.id,
                                            msg_id,
                                            reply_markup=await inline.quiz_inline_keyboard(quiz, msg_id))
        await callback.answer()





