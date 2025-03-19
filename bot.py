import os
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command

# Отримуємо токен з змінної середовища та видаляємо зайві пробіли
TOKEN = os.getenv("BOT_TOKEN", "").strip()

# Перевірка на наявність токена
if not TOKEN:
    raise ValueError("Токен бота не знайдено або він порожній! Перевірте налаштування змінної середовища.")

# Ініціалізація бота та диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Список підписників (set для унікальності)
subscribers = set()

# Обробник команди /start
@dp.message(Command("start"))
async def start_handler(message: Message):
    # Створення клавіатури
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button = KeyboardButton("Старт")
    keyboard.add(button)

    # Додаємо користувача до списку підписників
    if message.chat.id not in subscribers:
        subscribers.add(message.chat.id)
        await message.answer("Привіт! Ви підписалися на розсилку.", reply_markup=keyboard)
    else:
        await message.answer("Ви вже підписані.", reply_markup=keyboard)

# Обробник команди /subscribers для перегляду списку підписників
@dp.message(Command("subscribers"))
async def subscribers_handler(message: Message):
    if subscribers:
        subscribers_list = "\n".join(map(str, subscribers))
        await message.answer(f"Список підписників:\n{subscribers_list}")
    else:
        await message.answer("Немає підписників.")

# Основна асинхронна функція
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())