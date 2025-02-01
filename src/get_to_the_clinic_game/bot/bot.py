import asyncio
import logging
import os
from aiogram import Dispatcher, Bot
from aiogram.types import Message
from aiogram.utils.token import TokenValidationError


logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class Context:
    def __init__(self) -> None:
        self.counter = 0


dp = Dispatcher()


@dp.message()
async def echo(message: Message, context: Context) -> None:
    await message.reply(str(context.counter))
    context.counter += 1


async def main() -> None:
    try:
        TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
    except KeyError:
        logger.error(
            "Could not get bot token from environment: TELEGRAM_BOT_TOKEN is unset"
        )
        exit(1)

    try:
        logger.info("Creating bot")
        bot = Bot(TELEGRAM_BOT_TOKEN)
    except TokenValidationError:
        logger.exception("Telegram bot token validation error")
        exit(2)

    await dp.start_polling(bot, context=Context())


if __name__ == "__main__":
    asyncio.run(main())
