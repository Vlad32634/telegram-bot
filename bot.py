from aiogram import Bot, Dispatcher, Router, types
from aiogram.types import BotCommand, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
import asyncio
import os

TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_IDS = os.getenv("ADMIN_IDS", "")
WELCOME_PHOTO_URL = "https://www.dropbox.com/scl/fi/cdcdcurqd5drqazmb1qem/.jpg?rlkey=qelj9sfhpalt7xdynzbwoajxo&st=7cyakdtf&dl=0"  
if not TOKEN:
    raise ValueError("Токен бота не знайдено! Перевірте налаштування змінної середовища.")
if not ADMIN_IDS:
    raise ValueError("ADMIN_IDS не встановлено в змінних середовища.")

# Ініціалізація бота та диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()

# Список підписників
subscribers = set()

# Отримуємо список ID адміністратора із змінної середовища
ADMIN_IDS = os.getenv("ADMIN_IDS")

# Перевіряємо, чи є ADMIN_IDS у змінних середовища
if not ADMIN_IDS:
    print("❌ Не знайдено ADMIN_IDS у змінних середовища.")
else:
    print(f"ADMIN_IDS: {ADMIN_IDS}")

# Функція для перевірки, чи є користувач адміністратором
def is_admin(user_id):
    admin_ids = ADMIN_IDS.split(",") if ADMIN_IDS else []
    admin_ids = [admin_id.strip() for admin_id in admin_ids if admin_id.strip().isdigit()]
    return str(user_id) in admin_ids

# Функція для надсилання повідомлення адміністраторам
async def notify_admins(text):
    if not ADMIN_IDS:
        print("❌ Немає ID адміністратора у змінній середовища ADMIN_IDS.")
        return

    admin_ids = ADMIN_IDS.split(",")
    for admin_id in admin_ids:
        admin_id = admin_id.strip()
        if not admin_id.isdigit():
            print(f"❌ Невірний ID адміністратора: {admin_id}")
            continue

        try:
            await bot.send_message(admin_id, text)
        except Exception as e:
            print(f"❌ Не вдалося надіслати повідомлення адміну {admin_id}: {e}")
            
# Функція для налаштування команд
async def set_bot_commands():
    commands = [
        BotCommand(command="start", description="Запустити бота"),
        BotCommand(command="broadcast", description="Розсилка (тільки для адміністратора)"),
        BotCommand(command="subscribers", description="Список підписників (адмін)"),
    ]
    await bot.set_my_commands(commands)

async def notify_admin(text):
    try:
        await bot.send_message(ADMIN_IDS, text)
    except Exception as e:
        print(f"Не вдалося надіслати повідомлення адміну: {e}")

# Обробник команди /broadcast (розсилка)
@router.message(Command("broadcast"))
async def broadcast_handler(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас немає прав для виконання цієї команди.")
        return

    broadcast_text = (
        "Добрий день 😊\n\n"
        "Чи Вам не пора записатись на масаж? 💆‍♂️💆‍♀️\n"
        "Якщо Ви в мене вже були, для Вас знижка на масаж 20% до кінця цієї неділі! 🎉\n"
        "Якщо будете вперше, також знижка 20%! 🔥\n\n"
        "Подбайте про себе ❤️"
    )

    sent_count = 0
    for user_id in subscribers:
        try:
            await bot.send_message(user_id, broadcast_text)
            sent_count += 1
        except Exception as e:
            print(f"❌ Не вдалося надіслати повідомлення {user_id}: {e}")

    await message.answer(f"✅ Повідомлення надіслано {sent_count} користувачам.")

# Обробник команди /subscribers (список підписників)
@router.message(Command("subscribers"))
async def subscribers_handler(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас немає прав для перегляду підписників.")
        return

    if not subscribers:
        await message.answer("📋 Підписників ще немає.")
        return

    subscriber_list = "\n".join([f"🆔 {user_id}" for user_id in subscribers])
    await message.answer(f"📋 Список підписників:\n{subscriber_list}")

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

# Функція для створення головної клавіатури
def main_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Записатися на масаж")],
            [KeyboardButton(text="Опис масажів")],
            [KeyboardButton(text="Прайс")],
            [KeyboardButton(text="Перевірити статус")]
        ],
        resize_keyboard=True
    )
    return keyboard

# Обробник команди /start
@router.message(Command("start"))
async def start_handler(message: types.Message):
    user_id = str(message.from_user.id)
    username = f"@{message.from_user.username}" if message.from_user.username else "Без юзернейму"
    full_name = message.from_user.full_name
    
    if user_id not in subscribers:
        subscribers.add(user_id)
        await notify_admins(f"➕ Новий підписник: {message.from_user.full_name} (@{message.from_user.username}, ID: {user_id})")

    welcome_text = (
        "Привіт! Мене звати Влад, я масажист і реабілітолог 👨‍⚕️ з досвідом понад 5 років.\n"
        "В моєму телеграм-боті ви можете:\n"
        "✔ Отримати ЗНИЖКУ на масаж, просто натиснувши клавішу\n"
        "✔ Дізнатися все про види масажу і обрати який Вам підходить\n"
        "✔ Записатись на масаж\n"
        "✔ Переглянути прайс\n\n"
        "Обирайте потрібний розділ нижче 👇"
    )

    WELCOME_PHOTO_URL = "https://www.dropbox.com/scl/fi/cdcdcurqd5drqazmb1qem/.jpg?rlkey=qelj9sfhpalt7xdynzbwoajxo&st=7cyakdtf&dl=0"

    await bot.send_photo(message.chat.id, WELCOME_PHOTO_URL, caption=welcome_text, reply_markup=main_keyboard())
    
# Функція для надсилання повідомлення адміністраторам
async def notify_admins(text):
    for admin_id in ADMIN_IDS.split(","):
        try:
            await bot.send_message(admin_id.strip(), text)
        except Exception as e:
            print(f"❌ Не вдалося надіслати повідомлення адміну {admin_id}: {e}")

# Обробник кнопки "Записатися на масаж"
@router.message(lambda message: message.text.lower() == "записатися на масаж")
async def book_massage(message: types.Message):
    await message.answer("✅ Ви записалися на масаж. З вами зв'яжеться масажист.")
    await notify_admins(f"📅 Новий запис на масаж: {message.from_user.full_name} (@{message.from_user.username}, ID: {message.from_user.id})")

# Обробник кнопки "Перевірити статус"
@dp.message(lambda message: message.text.lower() == "перевірити статус")
async def check_status(message: types.Message):
    await message.answer("ℹ Ваш статус: Очікує підтвердження.")

# Обробник кнопки "Опис масажів"
@router.message(lambda message: message.text and message.text.lower() == "опис масажів")
async def show_massage_list(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=name)] for name in MASSAGE_DESCRIPTIONS.keys()
        ] + [[KeyboardButton(text="🔙 Назад")]],  # Додаємо кнопку "Назад"
        resize_keyboard=True
    )
    await message.answer("Оберіть вид масажу:", reply_markup=keyboard)

# Обробник кнопки "🔙 Назад"
@router.message(lambda message: message.text and message.text.lower() == "🔙 назад")
async def back_to_main(message: types.Message):
    await message.answer("🔙 Повертаємося в головне меню.", reply_markup=main_keyboard())
    
# Обробник вибору масажу
@router.message(lambda message: message.text in MASSAGE_DESCRIPTIONS)
async def show_massage_details(message: types.Message):
    massage_name = message.text
    massage = MASSAGE_DESCRIPTIONS[massage_name]
    await message.answer(
        massage["text"], 
        reply_markup=main_keyboard(),
        parse_mode="HTML",
        disable_web_page_preview=True
    )
    await message.answer_photo(massage["photo"])

# Обробник кнопки "Прайс"
@router.message(lambda message: message.text.lower() == "прайс")
async def show_price(message: types.Message):
    await message.answer_photo(PRICE_IMAGE_URL, caption="📋 Ось наш актуальний прайс на масажі.")

# Запуск бота
async def main():
    await set_bot_commands()
    dp.include_router(router)
    await notify_admin("✅ Бот запущено!")
    await dp.start_polling(bot)

# Стартуємо бота
if __name__ == "__main__":
    asyncio.run(main())
