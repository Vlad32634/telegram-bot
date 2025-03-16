import os
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Отримуємо токен із змінних середовища Railway
TOKEN = os.getenv("BOT_TOKEN")

# Перевіряємо, чи є токен (щоб уникнути помилок)
if not TOKEN:
    raise ValueError("BOT_TOKEN не знайдено! Додайте його в змінні середовища Railway.")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Список підписників (тимчасове збереження)
subscribers = set()

# Обробник команди /start
@dp.message(Command("start"))
async def start_handler(message: Message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    button = KeyboardButton("Старт")
    keyboard.add(button)

    # Додаємо користувача в список підписників
    if message.chat.id not in subscribers:
        subscribers.add(message.chat.id)
        await message.answer("Привіт! Ви підписалися на розсилку.", reply_markup=keyboard)
    else:
        await message.answer("Ви вже підписані.", reply_markup=keyboard)

# Обробник команди /subscribers для перегляду списку підписників
@dp.message(Command("subscribers"))
async def subscribers_handler(message: Message):
    if subscribers:
        subscribers_list = "\n".join([str(sub) for sub in subscribers])
        await message.answer(f"Список підписників:\n{subscribers_list}")
    else:
        await message.answer("Немає підписників.")

# Основна асинхронна функція
async def main():
    print("Бот запущений!")
    await dp.start_polling(bot)

# Правильний запуск бота
if __name__ == "__main__":
    asyncio.run(main())