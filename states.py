from aiogram.dispatcher.filters.state import State, StatesGroup


class CreateQuizStates(StatesGroup):
    is_anon = State()
    title = State()
    description = State()
    questions = State()


class ChangeQuizTitle(StatesGroup):
    get_new_title = State()


class ChangeQuizContent(StatesGroup):
    get_new_description = State()
