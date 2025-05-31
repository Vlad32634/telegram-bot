from aiogram import Bot, Dispatcher, Router, types
from aiogram.types import BotCommand, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
import asyncio
import os
import asyncpg

TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_IDS = os.getenv("ADMIN_IDS", "")
DATABASE_URL = os.getenv("DATABASE_URL")

WELCOME_PHOTO_URL = "https://www.dropbox.com/scl/fi/cdcdcurqd5drqazmb1qem/.jpg?rlkey=qelj9sfhpalt7xdynzbwoajxo&st=7cyakdtf&dl=0" 

if not TOKEN:
    raise ValueError("Токен бота не знайдено! Перевірте налаштування змінної середовища.")
if not ADMIN_IDS:
    raise ValueError("ADMIN_IDS не встановлено в змінних середовища.")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL не встановлено в змінних середовища.")
    
# Ініціалізація бота та диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()

# Функція для підключення до бази даних
async def create_pool():
    return await asyncpg.create_pool(dsn=DATABASE_URL)
    
async def load_subscribers_from_db():
    pool = await create_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT id FROM subscribers")
    await pool.close()
    return set(int(row["id"]) for row in rows)

async def create_tables():
    pool = await create_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS subscribers (
                id BIGINT PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                phone_number TEXT
            );
        """)
    await pool.close()
    
# Список підписників
subscribers = set()

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
            
# Функція для налаштування команд
async def set_bot_commands():
    commands = [
        BotCommand(command="start", description="Запустити бота"),
        BotCommand(command="broadcast", description="Розсилка (тільки для адміністратора)"),
        BotCommand(command="subscribers", description="Список підписників (адмін)"),
    ]
    await bot.set_my_commands(commands)

async def main():
    await create_tables()
    
    # Крок 2: оновлюємо глобальний список із бази
    global subscribers
    subscribers.update(await load_subscribers_from_db())

    # Крок 3: налаштовуємо команди
    await set_bot_commands()

    # Крок 4: додаємо роутер
    dp.include_router(router)

    # Крок 5: повідомляємо адміністраторів
    await notify_admins("✅ Бот запущено!")

    # Крок 6: стартуємо бота
    await dp.start_polling(bot)

# Обробник команди /broadcast (розсилка)
@router.message(Command("broadcast"))
async def broadcast_handler(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас немає прав для виконання цієї команди.")
        return

    broadcast_text = (
        "Привіт! 😊 Як настрій?\n\n"
        "Чи не болить в тебе спина чи голова часом? Бо я ж знаю як вирішити це питання\n"
        "Тим паче я тут завжди під боком\n"
        "Я завжди радий допомогти розслабитись і зарядитись енергією на масажі 💆‍♂️💆‍♀️"
)

    sent_count = 0
    for user_id in subscribers:
        try:
            await bot.send_message(user_id, broadcast_text)
            sent_count += 1
        except Exception as e:
            print(f"❌ Не вдалося надіслати повідомлення {user_id}: {e}")

    await message.answer(f"✅ Повідомлення надіслано {sent_count} користувачам.")

@router.message(Command("subscribers"))
async def subscribers_handler(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас немає прав для перегляду підписників.")
        return

    pool = await create_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT id, username, full_name, phone_number FROM subscribers")

    if not rows:
        await message.answer("📋 Підписників ще немає.")
        return

    lines = []
    for row in rows:
        line = f"🆔 {row['id']}"
        if row['username']:
            line += f" | @{row['username']}"
        if row['full_name']:
            line += f" | {row['full_name']}"
        if row['phone_number']:
            line += f" | 📞 {row['phone_number']}"
        lines.append(line)

    await message.answer("📋 Список підписників:\n\n" + "\n".join(lines))

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
            [KeyboardButton(text="🔥 ЗНИЖКА НА МАСАЖ 20%!")],  # Верхня кнопка
            [KeyboardButton(text="Записатися на масаж")],
            [KeyboardButton(text="Опис масажів")],
            [KeyboardButton(text="Прайс")],
            [KeyboardButton(text="Перевірити статус")],
            [KeyboardButton(text="📍 Локація")],  # Додаємо кнопку Локації
            [KeyboardButton(text="📞 Зв'язатися зі мною")]  # Додаємо кнопку в головне меню
        ],
        resize_keyboard=True
    )
    return keyboard
    
# Inline-кнопка для контакту
def contact_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📞 Написати мені в Telegram", url="https://t.me/trenersokalsky")]
        ]
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

    pool = await create_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO subscribers(id, username, full_name)
            VALUES($1, $2, $3)
            ON CONFLICT (id) DO UPDATE
            SET username = EXCLUDED.username,
                full_name = EXCLUDED.full_name
            """,
            int(user_id),
            message.from_user.username,
            message.from_user.full_name
        )
    await pool.close()

    await notify_admins(f"➕ Новий підписник: {full_name} ({username}, ID: {user_id})")

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
    await message.answer("📞 Якщо маєш питання або хочеш записатися, напиши мені в Telegram: [Зв’язатись](https://t.me/trenersokalsky)", parse_mode="Markdown")
    
# Функція для надсилання повідомлення адміністраторам
async def notify_admins(text):
    for admin_id in ADMIN_IDS.split(","):
        try:
            await bot.send_message(admin_id.strip(), text)
        except Exception as e:
            print(f"❌ Не вдалося надіслати повідомлення адміну {admin_id}: {e}")

# Обробник кнопки "ЗНИЖКА"
@router.message(lambda message: message.text == "🔥 ЗНИЖКА НА МАСАЖ 20%!")
async def discount_handler(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or "Немає юзернейму"
    full_name = message.from_user.full_name

    # Надсилаємо повідомлення користувачу
    await message.answer("🎉 Вам надано знижку 20%! Скористайтесь нею до кінця цього тижня.")

    # Сповіщення адміну
    admin_message = f"🔔 {full_name} (@{username}, ID: {user_id}) натиснув(ла) на кнопку 'ЗНИЖКА НА МАСАЖ 20%'!"
    await notify_admins(admin_message)
    
@router.message(lambda message: message.text and message.text.lower() == "записатися на масаж")
async def ask_for_contact(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📞 Надіслати номер телефону", request_contact=True)],
            [KeyboardButton(text="🔙 Назад")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer(
        "Щоб записатись на масаж, будь ласка, надішліть свій номер телефону 👇",
        reply_markup=keyboard
    )

# Обробник кнопки "Перевірити статус"
@dp.message(lambda message: message.text and message.text.lower() == "перевірити статус")
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
@router.message(lambda message: message.text and message.text.lower() == "прайс")
async def show_price(message: types.Message):
    await message.answer_photo(PRICE_IMAGE_URL, caption="📋 Ось наш актуальний прайс на масажі.")

# Обробник кнопки "📍 Локація"
@router.message(lambda message: message.text == "📍 Локація")
async def location_handler(message: types.Message):
    google_maps_url = "https://maps.app.goo.gl/Z87zYbuceo9ijMwA8"  # Замініть на своє посилання
    address_text = "📍 Адреса: вул. Віталія Нестеренка 1Б, 1 будинок, салон 'Happy Family', Одеські Традиції"

    await message.answer(f"{address_text}\n\n🌍 Google Maps: {google_maps_url}")

# Обробник кнопки "Зв'язатися зі мною"
@router.message(lambda message: message.text == "📞 Зв'язатися зі мною")
async def contact_handler(message: types.Message):
    await message.answer("📞 Якщо у вас є питання, зв’яжіться зі мною:", reply_markup=contact_keyboard())

@router.message(lambda message: message.contact is not None)
async def process_contact(message: types.Message):
    user_id = message.from_user.id
    phone = message.contact.phone_number
    username = message.from_user.username or "Немає юзернейму"
    full_name = message.from_user.full_name

    # Збереження в базу
    pool = await create_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO subscribers(id, username, full_name, phone_number)
            VALUES($1, $2, $3, $4)
            ON CONFLICT (id) DO UPDATE
            SET username = EXCLUDED.username,
                full_name = EXCLUDED.full_name,
                phone_number = EXCLUDED.phone_number
            """,
            user_id,
            username,
            full_name,
            phone
        )
    await pool.close()

    # Відповідь користувачу
    await message.answer("✅ Ви записалися на масаж! З вами зв'яжеться масажист.")

    # Сповіщення адміну
    await notify_admins(f"📅 Запис на масаж: {full_name} (@{username}) | 📞 {phone}")
    
# Стартуємо бота
if __name__ == "__main__":
    asyncio.run(main())
    
