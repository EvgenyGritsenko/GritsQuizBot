from connection_bot import *
from handlers import answer_system, quiz_system


async def add_proxy_data(state, data: dict):
    async with state.proxy() as proxy:
        for k, v in data.items():
            proxy[k] = v


def on_startup():
    print('Бот запущен!')


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True,
                           on_startup=on_startup())
