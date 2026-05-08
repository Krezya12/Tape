import asyncio
import logging
import sys
from os import getenv

from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, html, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.utils.i18n import gettext as _, I18n, lazy_gettext as __, FSMI18nMiddleware

from apps.models import *

load_dotenv()

i18n = I18n(path="locales", default_locale="ru", domain="messages")
TOKEN = getenv("BOT_TOKEN")
dp = Dispatcher()


@dp.message_handler(commands=['start'])
async def send_welcome(message: Message):
    await message.reply("Привет! Введите ваш логин, чтобы получать уведомления об оценках.")


@dp.message_handler()
async def link_parent(message: Message):
    login = message.text.strip()

    try:
        # Ищем родителя по логину
        parent = User.objects.get(username=login, role='parent')

        # Сохраняем его Telegram ID
        parent.telegram_id = message.from_user.id
        parent.save()

        await message.reply(f"Успешно! Теперь вы будете получать отчеты для {parent.first_name} {parent.last_name}.")
    except User.DoesNotExist:
        await message.reply("Пользователь с таким логином не найден. Проверьте правильность написания.")

async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp.update.outer_middleware(FSMI18nMiddleware(i18n))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())