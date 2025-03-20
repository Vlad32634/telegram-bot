from aiogram import Bot, Dispatcher
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, BotCommand
from aiogram.filters import Command
import os
import asyncio

# Отримуємо токен з змінної середовища та видаляємо зайві пробіли
TOKEN = os.getenv("BOT_TOKEN", "").strip()
ADMIN_ID = os.getenv("ADMIN_ID", "").strip()

# Перевірка на наявність токена
if not TOKEN:
    raise ValueError("Токен бота не знайдено або він порожній! Перевірте налаштування змінної середовища.")

# Ініціалізація бота та диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Список підписників (set для унікальності)
subscribers = set()

async def set_bot_commands():
    commands = [
        BotCommand(command="start", description="Запустити бота"),
        BotCommand(command="broadcast", description="Розсилка повідомлень (тільки для адміністратора)")
    ]
    await bot.set_my_commands(commands)

# Обробник команди /start
@dp.message(Command("start"))
async def start_handler(message: Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Старт")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    if message.chat.id not in subscribers:
        subscribers.add(message.chat.id)
        await message.answer("Привіт! Ви підписалися на розсилку.", reply_markup=keyboard)
    else:
        await message.answer("Ви вже підписані.", reply_markup=keyboard)

# Обробник команди /broadcast
@dp.message(Command("broadcast"))
async def broadcast_handler(message: Message):
    if str(message.chat.id) != ADMIN_ID:  # Перевіряємо, чи це адміністратор
        await message.answer("У вас немає прав для виконання цієї команди.")
        return
    
    text = "📢 Спеціальна пропозиція! Записуйтесь на масаж сьогодні та отримуйте знижку!"
    
    for user_id in subscribers:
        try:
            await bot.send_message(user_id, text)
        except Exception as e:
            print(f"Не вдалося надіслати повідомлення {user_id}: {e}")
    
    await message.answer("Розсилка завершена!")

# Основна асинхронна функція
async def main():
    await set_bot_commands()  # Додаємо список команд у Telegram
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())