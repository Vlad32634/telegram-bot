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
            [KeyboardButton(text="Опис масажів")],
        ],
        resize_keyboard=True
    )

# Клавіатура для опису масажів
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_massage_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Класичний масаж")],
            [KeyboardButton(text="Лімфодренажний масаж")],
            [KeyboardButton(text="Антицелюлітний масаж")],
            [KeyboardButton(text="Лікувальний масаж")],
            [KeyboardButton(text="Міофасціальний масаж")],
            [KeyboardButton(text="Вакуумний масаж")],
            [KeyboardButton(text="Креольський масаж")],
            [KeyboardButton(text="⬅ Назад")]
        ],
        resize_keyboard=True
    )
    return keyboard

MASSAGE_DESCRIPTIONS = {
    "Класичний масаж": {
        "text": "🔹 Класичний масаж покращує кровообіг, знімає напругу м’язів та сприяє загальному розслабленню.",
        "photo": "https://www.dropbox.com/scl/fi/n74kdxul6vqv995tkvrbm/photo_2025-03-22_14-09-52.jpg?rlkey=lh7h8hpzytjyuhxzs22qkg1z6&st=vtixsvbg&dl=0"
    },
    "Лімфодренажний масаж": {
        "text": "🔹 Лімфодренажний масаж допомагає вивести зайву рідину, зменшити набряки та покращити обмін речовин.",
        "photo": "https://www.dropbox.com/scl/fi/w74j44zoxlbqzrabnze3s/photo_2025-03-22_14-09-37.jpg?rlkey=4l22scog50x46vcga56glqobf&st=2n978nt4&dl=0"
    },
    "Антицелюлітний масаж": {
        "text": "🔹 Антицелюлітний масаж спрямований на зменшення целюліту та покращення стану шкіри.",
        "photo": "https://www.dropbox.com/scl/fi/d8d34lezl9ge2hlkkuxue/photo_2025-03-22_14-09-40.jpg?rlkey=wkb3ksrjf25kj50z89jy80qnw&st=b24bzdat&dl=0"
    },
    "Лікувальний масаж": {
        "text": "🔹 Лікувальний масаж допомагає зменшити біль у м’язах, поліпшити рухливість суглобів та відновити після травм.",
        "photo": "https://www.dropbox.com/scl/fi/60sv4y1kclksev8prax8q/photo_2025-03-22_14-09-43.jpg?rlkey=lanlkah8i13b1ybbmtrvo2hrv&st=n7hf2trt&dl=0"
    },
    "Міофасціальний масаж": {
        "text": "🔹 Міофасціальний масаж працює з глибокими тканинами, розслаблюючи м’язові затиски та покращуючи еластичність.",
        "photo": "https://www.dropbox.com/scl/fi/zt684u4jbys916pb058q1/photo_2025-03-22_14-09-46.jpg?rlkey=ytv7yxle9hynmyznct6tbynhr&st=96ook5os&dl=0"
    },
    "Вакуумний масаж": {
        "text": "🔹 Вакуумний масаж стимулює кровообіг, допомагає позбутися застійних явищ та покращує стан шкіри.",
        "photo": "https://www.dropbox.com/scl/fi/ip6fxmwsnhadynfxad4a6/photo_2025-03-22_14-09-48.jpg?rlkey=rebf46es2hatcfqv2z1dndh8i&st=9hyufeth&dl=0"
    },
    "Креольський масаж": {
        "text": "🔹 Креольський масаж виконується за допомогою спеціальних бамбукових паличок для глибокого впливу на тканини.",
        "photo": "https://www.dropbox.com/scl/fi/ped1ssk7o1awe2i3n9pvv/photo_2025-03-22_14-09-50.jpg?rlkey=ifotepuj04tex8w9vr9kc707b&st=lk0l5oq9&dl=0"
  }
}

# Посилання на зображення прайсу
PRICE_IMAGE_URL = "https://www.dropbox.com/scl/fi/z25kakyigrnuoz5idl1hv/photo_2025-03-20_16-16-36.jpg?rlkey=tszprs745na564o1m9ku5jz26&st=td8us3zu&dl=0"

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

# Обробник кнопки "Записатися на масаж"
@dp.message(lambda message: message.text and message.text.lower() == "записатися на масаж")
async def book_massage(message: types.Message):
    user_id = message.chat.id
    username = message.from_user.username or "Немає юзернейму"
    
    massage_bookings[user_id] = {
        "status": "Очікує підтвердження",
        "username": username,
        "phone": subscribers.get(user_id, {}).get("phone", "Немає номера")
    }

    await message.answer("✅ Ви записалися на масаж. З вами зв'яжеться масажист.")

    # Сповіщення адміну
    admin_message = (
        f"✍ *Новий запис на масаж!*\n"
        f"👤 ID: `{user_id}`\n"
        f"💬 Юзернейм: @{username}\n"
        f"📞 Телефон: {massage_bookings[user_id]['phone']}"
    )
    await bot.send_message(ADMIN_ID, admin_message, parse_mode="Markdown")

# Обробник кнопки "Перевірити статус"
@dp.message(lambda message: message.text and message.text.lower() == "перевірити статус")
async def check_status(message: types.Message):
    user_id = message.chat.id
    booking = massage_bookings.get(user_id)

    if booking:
        await message.answer(f"📌 *Ваш статус:* {booking['status']}", parse_mode="Markdown")
    else:
        await message.answer("ℹ У вас немає запису на масаж. Ви можете записатися через меню.")

# Функція для створення клавіатури з масажами
def get_massage_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    for name in MASSAGE_DESCRIPTIONS.keys():
        keyboard.add(KeyboardButton(text=name))
    return keyboard

@dp.message(lambda message: message.text == "Опис масажів")
async def show_massage_list(message: types.Message):
    keyboard = get_massage_keyboard()
    await message.answer("Оберіть вид масажу:", reply_markup=keyboard)
    
# Обробник кнопок з описом масажів
@dp.message(lambda message: message.text in MASSAGE_DESCRIPTIONS)
async def massage_description_handler(message: types.Message):
    massage_type = message.text.strip()
    
    if massage_type in MASSAGE_DESCRIPTIONS:
        description = MASSAGE_DESCRIPTIONS[massage_type]["text"]
        photo = MASSAGE_DESCRIPTIONS[massage_type]["photo"]

        await message.answer_photo(photo, caption=description)
    else:
        await message.answer("Будь ласка, виберіть масаж із кнопок.")

# Обробка кнопки "Назад"
@dp.message(lambda message: message.text == "⬅ Назад")
async def back_to_main_menu(message: types.Message):
    await message.answer("🔙 Повернення до головного меню", reply_markup=main_keyboard())

# Обробник кнопки "Прайс"
@dp.message(lambda message: message.text.lower() == "прайс")
async def show_price(message: types.Message):
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
