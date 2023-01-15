from aiogram.dispatcher import FSMContext
from connection_bot import bot, dp
from aiogram import types
import states
from keyboards import ususally, inline
from aiogram.types import ReplyKeyboardRemove
from main import add_proxy_data
from aiogram.types.input_file import InputFile
import data_base


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
    await message.reply(str(clean_questions), reply=False)
    quiz = data_base.create_quiz(await state.get_data())
    for q in clean_questions:
        data_base.create_question({'question': q, 'quiz_id': quiz})
    await message.reply('Опрос успешно добавлен!', reply=False)
    await state.finish()


