import keyboards.inline
from connection_bot import *
from aiogram import types
from handlers import answer_system, quiz_system
from aiogram.dispatcher.filters import Text


async def add_proxy_data(state, data: dict):
    async with state.proxy() as proxy:
        for k, v in data.items():
            proxy[k] = v


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.reply('С помощью данного бота можно создавать опросы.\n'
                        'Если вам нужно пройти опрос, введите /answer_questions\n'
                        'Если нужно создать опрос, введите /create_quiz \n'
                        'Помощь по боту - /help', reply=False)


@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    await message.reply('Выберите нужный пункт', reply=False,
                        reply_markup=await keyboards.inline.help_inline_keyboard())


@dp.callback_query_handler(Text('help_answer_questions'))
async def help_answer_questions(callback: types.CallbackQuery):
    message = '✅ Чтобы вам пройти опрос, нужно заранее узнаеть его ID.\n' \
              'Далее введите команду /answer_questions и следуйте инструкциям.\n' \
              'Отвечая на вопросы вам нужно вводить ответы на вопросы через запятую, ' \
              'вот так: Ответ1, Ответ2, Ответ3\nИ вводить ответы нужно в той ' \
              'последовательности в которой расположены вопросы.'
    await bot.send_message(callback.message.chat.id, message)
    await callback.answer()


@dp.callback_query_handler(Text('help_create_quiz'))
async def help_answer_questions(callback: types.CallbackQuery):
    message = '✅ Для создания своего опроса введите команду /create_quiz\n' \
              'Далее просто следуйте инструкциям. Но обратите внимание на ' \
              'указание вопросов. Вводите их просто через запятую: ' \
              'Вопрос1, Вопрос2, Вопрос3'
    await bot.send_message(callback.message.chat.id, message)
    await callback.answer()


@dp.callback_query_handler(Text('help_my_quiz'))
async def help_answer_questions(callback: types.CallbackQuery):
    message = '✅ Чтобы удалить, редактировать, получить статистику ответов ' \
              'на ваши опросы, введите /my_quiz \n' \
              'Статистика ответов будет приходить в виде Excel файла и для каждого ' \
              'вопроса будет создан отдельный лист ответов.'
    await bot.send_message(callback.message.chat.id, message)
    await callback.answer()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
