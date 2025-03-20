from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, BotCommand
from aiogram.filters import Command
import os
import asyncio

# Отримуємо токен з змінної середовища та видаляємо зайві пробіли
TOKEN = os.getenv("BOT_TOKEN", "").strip()
ADMIN_ID = os.getenv("ADMIN_ID", "").strip()

if not TOKEN:
    raise ValueError("Токен бота не знайдено або він порожній! Перевірте налаштування змінної середовища.")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Список підписників та записів
subscribers = {}
massage_bookings = {}

# Команди бота
async def set_bot_commands():
    commands = [
        BotCommand(command="start", description="Запустити бота"),
        BotCommand(command="broadcast", description="Розсилка (тільки для адміністратора)"),
        BotCommand(command="subscribers", description="Список підписників (адмін)")
    ]
    await bot.set_my_commands(commands)

# Головне меню
def main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Записатися на масаж")],
            [KeyboardButton(text="Перевірити статус")],
            [KeyboardButton(text="Прайс")],
            [KeyboardButton(text="Поділитися номером", request_contact=True)]
        ],
        resize_keyboard=True
    )

# Обробник команди /start
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    user_id = message.chat.id
    username = message.from_user.username or "Немає юзернейму"

    if user_id not in subscribers:
        subscribers[user_id] = {"username": username, "phone": None}
        await message.answer("Привіт! Ви підписалися на бота.", reply_markup=main_keyboard())

        # Сповіщення адміну
        admin_message = f"🔔 *Нова підписка!*\n👤 ID: `{user_id}`\n💬 Юзернейм: @{username}"
        await bot.send_message(ADMIN_ID, admin_message, parse_mode="Markdown")
    else:
        await message.answer("Ви вже підписані.", reply_markup=main_keyboard())

# Обробник отримання номера телефону
@dp.message(lambda message: message.contact)
async def handle_contact(message: types.Message):
    user_id = message.chat.id
    phone_number = message.contact.phone_number

    if user_id in subscribers:
        subscribers[user_id]["phone"] = phone_number

    # Сповіщення адміну
    admin_message = f"📱 *Отримано контакт від користувача*\n👤 ID: `{user_id}`\n📞 Телефон: {phone_number}"
    await bot.send_message(ADMIN_ID, admin_message, parse_mode="Markdown")

    await message.answer("Дякуємо! Ваш номер збережено.")

# Обробник кнопки "Записатися на масаж"
@dp.message(lambda message: message.text.lower() == "записатися на масаж")
async def book_massage(message: types.Message):
    user_id = message.chat.id
    username = message.from_user.username or "Немає юзернейму"
    
    massage_bookings[user_id] = "Очікує підтвердження"

    await message.answer("Ви записалися на масаж. З вами зв'яжеться масажист.")

    # Сповіщення адміну
    admin_message = f"✍ *Новий запис на масаж!*\n👤 ID: `{user_id}`\n💬 Юзернейм: @{username}"
    await bot.send_message(ADMIN_ID, admin_message, parse_mode="Markdown")

# Обробник кнопки "Перевірити статус"
@dp.message(lambda message: message.text.lower() == "перевірити статус")
async def check_status(message: types.Message):
    status = massage_bookings.get(message.chat.id, "У вас немає запису на масаж.")
    await message.answer(f"📌 *Ваш статус:* {status}")

# Обробник кнопки "Прайс"
@dp.message(lambda message: message.text.lower() == "прайс")
async def show_price(message: types.Message):
    PRICE_IMAGE_URL = "https://www.dropbox.com/scl/fi/z25kakyigrnuoz5idl1hv/photo_2025-03-20_16-16-36.jpg?rlkey=tszprs745na564o1m9ku5jz26&st=td8us3zu&dl=0" 

    try:
        await message.answer_photo(PRICE_IMAGE_URL, caption="Ось наш прайс 📋")
    except Exception as e:
        await message.answer("⚠ Виникла помилка при відправці прайсу.")
        print(f"Помилка: {e}")

# Обробник команди /subscribers (тільки для адміністратора)
@dp.message(Command("subscribers"))
async def list_subscribers(message: types.Message):
    if str(message.chat.id) != ADMIN_ID:
        await message.answer("У вас немає прав для виконання цієї команди.")
        return

    if not subscribers:
        await message.answer("📋 Список підписників порожній.")
        return

    response = "📋 *Список підписників:*\n"
    for user_id, info in subscribers.items():
        response += f"👤 ID: `{user_id}`\n💬 Юзернейм: @{info['username']}\n📞 Телефон: {info['phone'] or 'Немає'}\n\n"
    
    await message.answer(response, parse_mode="Markdown")

# Основна асинхронна функція
async def main():
    await set_bot_commands()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
