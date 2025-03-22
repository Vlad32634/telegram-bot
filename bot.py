from aiogram import Bot, Dispatcher, Router, types
from aiogram.types import BotCommand, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
import asyncio
import os

TOKEN = os.getenv("BOT_TOKEN", "")

if not TOKEN:
    raise ValueError("Токен бота не знайдено! Перевірте налаштування змінної середовища.")

# Ініціалізація бота та диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()  # Dispatcher створюється без аргументів
router = Router()  # Окремий Router для хендлерів

# Функція для налаштування команд
async def set_bot_commands():
    commands = [
        BotCommand(command="start", description="Запустити бота"),
        BotCommand(command="broadcast", description="Розсилка (тільки для адміністратора)"),
        BotCommand(command="subscribers", description="Список підписників (адмін)"),
    ]
    await bot.set_my_commands(commands)

# Головне меню
def main_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Записатися на масаж")],
            [KeyboardButton(text="Перевірити статус")],
            [KeyboardButton(text="Прайс")],
            [KeyboardButton(text="Опис масажів")]
        ],
        resize_keyboard=True
    )  
    return keyboard  
    
# Опис масажів
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

# Обробник команди /start (реєструємо його у router, а не в dp)
@router.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("Привіт! Я бот для запису на масаж.", reply_markup=main_keyboard())
    
# Обробник кнопки "Записатися на масаж"
@dp.message(lambda message: message.text.lower() == "записатися на масаж")
async def book_massage(message: types.Message):
    await message.answer("✅ Ви записалися на масаж. З вами зв'яжеться масажист.")

# Обробник кнопки "Перевірити статус"
@dp.message(lambda message: message.text.lower() == "перевірити статус")
async def check_status(message: types.Message):
    await message.answer("ℹ Ваш статус: Очікує підтвердження.")

# Обробник кнопки "Опис масажів"
@dp.message(lambda message: message.text.lower() == "опис масажів")
async def show_massage_list(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=name)] for name in MASSAGE_DESCRIPTIONS.keys()],
        resize_keyboard=True
    )
    await message.answer("Оберіть вид масажу:", reply_markup=keyboard)

# Обробник вибору конкретного масажу
@dp.message(lambda message: message.text in MASSAGE_DESCRIPTIONS)
async def massage_description_handler(message: types.Message):
    massage_type = message.text.strip()
    
    if massage_type in MASSAGE_DESCRIPTIONS:
        description = MASSAGE_DESCRIPTIONS[massage_type]["text"]
        photo = MASSAGE_DESCRIPTIONS[massage_type]["photo"]
        await message.answer_photo(photo, caption=description)
    else:
        await message.answer("Будь ласка, виберіть масаж із кнопок.")

# Обробник кнопки "Прайс"
@dp.message(lambda message: message.text.lower() == "прайс")
async def show_price(message: types.Message):
    try:
        await message.answer_photo(PRICE_IMAGE_URL, caption="Ось наш прайс 📋")
    except Exception as e:
        await message.answer("⚠ Виникла помилка при відправці прайсу.")
        print(f"Помилка: {e}")

# Головна асинхронна функція
async def main():
    dp.include_router(router)  # Додаємо router в Dispatcher
    await set_bot_commands()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
