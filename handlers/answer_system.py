import data_base
import keyboards.ususally
import states
from connection_bot import bot, dp
from aiogram import types
from states import AnswerQuestion
from data_base import get_all_links_id
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove

QUIZ_ID = None


@dp.message_handler(commands=['answer_questions'])
async def answer_questions_command(message: types.Message):
    await message.reply('Введите ссылку(id) опроса, чтобы пройти его', reply=False)
    await AnswerQuestion.get_quiz_id.set()


@dp.message_handler(state=AnswerQuestion.get_quiz_id)
async def get_quiz_id_state(message: types.Message, state: FSMContext):
    global QUIZ_ID
    try:
        link_id = int(message.text)
        all_id = get_all_links_id()
        if int(link_id) in all_id:
            link = int(link_id)
            quiz = data_base.find_by_link(link)[0]
            QUIZ_ID = quiz.id
            anon_status = quiz.is_anonymous
            if anon_status:
                await message.reply(f'Опрос "{quiz.title}" содержит {len(quiz.questions)} вопросов.\n'
                                    f'Данный опрос АНОНИМНЫЙ, ваши данные не будут видны.\n'
                                    f'Начать прохождение?',
                                    reply=False,
                                    reply_markup=keyboards.ususally.start_passing_quiz())
            else:
                await message.reply(f'Опрос "{quiz.title}" содержит {len(quiz.questions)} вопросов.\n'
                                    f'Данный опрос ПУБЛИЧНЫЙ, ваши данные (ник, имя, фамилия профиля, '
                                    f'время прохождения) будут видны создателю опроса.\n'
                                    f'Начать прохождение?',
                                    reply=False,
                                    reply_markup=keyboards.ususally.start_passing_quiz())
            await states.PassingQuiz().start.set()
        else:
            await message.reply('Такого опроса не существует! Уточните ID и повторите попытку', reply=False)
            await state.finish()
    except (IndexError, ValueError):
        await message.reply('ID состоит из цифр! Повторите попытку', reply=False)
        await state.finish()


@dp.message_handler(state=states.PassingQuiz.start)
async def passing_quiz_start(message: types.Message, state: FSMContext):
    if message.text.lower() == 'начать':
        await message.reply('Введите через запятую ответы на вопросы, в порядке их расположения', reply=False,
                            reply_markup=ReplyKeyboardRemove())
        current_questions = str(data_base.get_quiz_questions(QUIZ_ID)).replace('[', '') \
            .replace(']', '').replace("'", '')
        await bot.send_message(message.from_user.id, f'Вопросы: \n{current_questions}')
        await states.PassingQuiz.next()
    else:
        await message.reply('Прохождение опроса отменено', reply=False,
                            reply_markup=ReplyKeyboardRemove())
        await state.finish()


@dp.message_handler(state=states.PassingQuiz.answer_the_questions, content_types=['text'])
async def answer_states_handler(message: types.Message, state: FSMContext):
    quiz = data_base.get_quiz(QUIZ_ID)
    questions_id = [i.id for i in quiz.questions]
    answers_list = message.text.split(',')
    answers_without_spaces = list(map(str.strip, answers_list))
    clean_answers = list(filter(None, answers_without_spaces))[:len(quiz.questions)]

    if quiz.is_anonymous:
        username_for_db = "Анонимно"
    else:
        username_for_db = message.from_user.full_name

    if len(clean_answers) >= len(quiz.questions):
        for a in clean_answers:
            data_base.create_answer({'user_id': message.from_user.id, 'quiz_id': QUIZ_ID,
                                    'username': username_for_db, 'answer': a,
                                     'question_id': questions_id[0]})
            questions_id.pop(0)
        await message.reply('Ответы отправлены!', reply=False)
        await state.finish()
    else:
        await message.reply('Вы ответили не на все вопросы, введите ответы заного!', reply=False)


