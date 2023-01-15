from aiogram.dispatcher.filters.state import State, StatesGroup


class CreateQuizStates(StatesGroup):
    is_anon = State()
    title = State()
    description = State()
    questions = State()
