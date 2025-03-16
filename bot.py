import os
import os
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Отримуємо токен з змінної середовища та видаляємо зайві пробіли
TOKEN = os.getenv("BOT_TOKEN", "").strip()

# Перевірка на наявність токена
if not TOKEN:
    raise ValueError("Токен бота не знайдено або він порожній! Перевірте налаштування змінної середовища.")

# Ініціалізація бота та диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Список підписників
subscribers = []

# Обробник команди /start
@dp.message(Command("start"))
async def start_handler(message: Message):
    # Створення клавіатури з параметром resize_keyboard
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    button = KeyboardButton("Старт")
    keyboard.add(button)

    # Перевірка, чи підписаний користувач
    if message.chat.id not in subscribers:
        subscribers.append(message.chat.id)
        await message.answer("Привіт! Ви підписалися на розсилку.", reply_markup=keyboard)
    else:
        await message.answer("Ви вже підписані.", reply_markup=keyboard)

# Обробник команди /subscribers для перегляду списку підписників
@dp.message(Command("subscribers"))
async def subscribers_handler(message: Message):
    if subscribers:
        # Вивести список підписників
        subscribers_list = "\n".join([str(sub) for sub in subscribers])
        await message.answer(f"Список підписників:\n{subscribers_list}")
    else:
        await message.answer("Немає підписників.")

# Основна асинхронна функція
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())