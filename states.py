from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.helper import Helper, HelperMode, ListItem


class CreateQuizStates(StatesGroup):
    is_anon = State()
    title = State()
    description = State()
    questions = State()


class ChangeQuizTitle(StatesGroup):
    get_new_title = State()


class ChangeQuizContent(StatesGroup):
    get_new_description = State()


class ChangeQuizQuestions(StatesGroup):
    get_new_questions = State()


class AnswerQuestion(StatesGroup):
    get_quiz_id = State()


class PassingQuiz(StatesGroup):
    start = State()
    answer_the_questions = State()

