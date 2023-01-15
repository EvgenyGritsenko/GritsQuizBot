from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage


bot = Bot(token='5842346573:AAFGv9BZrFfBWgzFPoltUCaPuvIAibxJdwI')
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

