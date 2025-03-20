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

# Список записів на масаж
appointments = {}

# ID адміністратора 
ADMIN_ID = os.getenv("ADMIN_ID")
if not ADMIN_ID:
    raise ValueError("ADMIN_ID не задано! Вкажіть ваш Telegram ID у змінній середовища.")

# Основна клавіатура
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Записатися на масаж")],
        [KeyboardButton(text="Переглянути мій запис")],
        [KeyboardButton(text="Список підписників")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

# Обробник команди /start
@dp.message(Command("start"))
async def start_handler(message: Message):
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

# Обробник кнопки "Записатися на масаж"
@dp.message(lambda msg: msg.text == "Записатися на масаж")
async def book_appointment(message: Message):
    appointments[message.chat.id] = "З вами зараз зв'яжеться масажист для запису"
    await message.answer("З вами зараз зв'яжеться масажист для запису.")
    # Сповіщення адміністратору
    await bot.send_message(ADMIN_ID, f"Нова заявка на масаж від @{message.from_user.username} (ID: {message.chat.id})")

# Обробник кнопки "Переглянути мій запис"
@dp.message(lambda msg: msg.text == "Переглянути мій запис")
async def check_appointment(message: Message):
    if message.chat.id in appointments:
        await message.answer("Ваш запис: ✅")
    else:
        await message.answer("Ви ще не записані.")

# Основна асинхронна функція
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
