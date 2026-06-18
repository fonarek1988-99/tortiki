import asyncio
import json
import os
from copy import deepcopy
from aiogram import Bot, Dispatcher, F, types
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    FSInputFile,
    CallbackQuery,
    Message
)

from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage


# =====================================
# НАСТРОЙКИ
# =====================================

ADMIN_ID = 6770764111

CONDITER_LINK = "https://t.me/repamaster"

bot = None

BOT_CITIES = {}

dp = Dispatcher(
    storage=MemoryStorage()
)


# =====================================
# ПАПКИ И ФАЙЛЫ
# =====================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

CATALOG_FILE = os.path.join(
    BASE_DIR,
    "catalog.json"
)

ORDERS_FILE = os.path.join(
    BASE_DIR,
    "orders.json"
)

USERS_FILE = os.path.join(
    BASE_DIR,
    "users.json"
)

PHOTOS_DIR = os.path.join(
    BASE_DIR,
    "photos"
)

PORTFOLIO_DIR = os.path.join(
    BASE_DIR,
    "portfolio"
)
import sqlite3

DB_FILE = "users.db"

conn = sqlite3.connect(
    DB_FILE,
    check_same_thread=False
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER,
    city TEXT,
    first_name TEXT,
    username TEXT
)
""")

conn.commit()

os.makedirs(PHOTOS_DIR, exist_ok=True)
os.makedirs(PORTFOLIO_DIR, exist_ok=True)


# =====================================
# СОЗДАНИЕ ФАЙЛОВ
# =====================================

if not os.path.exists(CATALOG_FILE):

    with open(
        CATALOG_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump({

            "cakes_children": [],
            "cakes_wedding": [],
            "cakes_holiday": [],
            "cakes_custom": [],
            "cakes_bento": [],
            "cakes_premium": [],

            "cupcakes_classic": [],
            "cupcakes_chocolate": [],
            "cupcakes_berry": [],
            "cupcakes_sets": [],

            "desserts_cheesecake": [],
            "desserts_brownie": [],
            "desserts_trifle": [],
            "desserts_cakepops": [],
            "desserts_macarons": [],
            "desserts_cookies": [],

            "gift_boxes": [],
            "gift_romantic": [],
            "gift_kids": [],
            "gift_birthday": [],

            "portfolio": []

        }, f, ensure_ascii=False, indent=4)


if not os.path.exists(ORDERS_FILE):

    with open(
        ORDERS_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            [],
            f,
            ensure_ascii=False,
            indent=4
        )


if not os.path.exists(USERS_FILE):

    with open(
        USERS_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            [],
            f,
            ensure_ascii=False,
            indent=4
        )


# =====================================
# ЗАГРУЗКА ДАННЫХ
# =====================================

def load_catalog():

    with open(
        CATALOG_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def save_catalog(data):

    with open(
        CATALOG_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=4
        )


def load_orders():

    with open(
        ORDERS_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def save_orders(data):

    with open(
        ORDERS_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=4
        )


def load_users():

    with open(
        USERS_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def save_users(data):

    with open(
        USERS_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=4
        )


# =====================================
# FSM
# =====================================

class AddProduct(StatesGroup):

    category = State()
    name = State()
    price = State()
    photo = State()


class Broadcast(StatesGroup):

    text = State()


class ReplyUser(StatesGroup):

    user_id = State()
    text = State()


class Consultation(StatesGroup):

    product_type = State()
    date = State()
    guests = State()
    wishes = State()
class AddPortfolio(StatesGroup):
    photo = State()

class DeleteProduct(StatesGroup):
    product = State()

class EditCardPrice(StatesGroup):
    category = State()
    index = State()
    price = State()
class ChangePrice(StatesGroup):
    product = State()
    price = State()
CATEGORY_NAMES = {
    "cakes_children": "🎂 Детские торты",
    "cakes_wedding": "💍 Свадебные торты",
    "cakes_holiday": "🎉 Праздничные торты",
    "cakes_custom": "🎨 Индивидуальный дизайн",
    "cakes_bento": "🍰 Бенто-торты",
    "cakes_premium": "👑 Премиум торты",

    "cupcakes_classic": "🧁 Классические",
    "cupcakes_chocolate": "🍫 Шоколадные",
    "cupcakes_berry": "🍓 Ягодные",
    "cupcakes_sets": "🎉 Наборы капкейков",

    "desserts_cheesecake": "🍰 Чизкейки",
    "desserts_brownie": "🍫 Брауни",
    "desserts_trifle": "🥤 Трайфлы",
    "desserts_cakepops": "🍭 Кейк-попсы",
    "desserts_macarons": "🌈 Макаронс",
    "desserts_cookies": "🍪 Печенье ручной работы",

    "gift_boxes": "🎁 Подарочные боксы",
    "gift_romantic": "❤️ Романтические наборы",
    "gift_kids": "👶 Детские наборы",
    "gift_birthday": "🎂 Наборы на праздник"
}
# =====================================
# КНОПКИ
# =====================================

def main_menu():

    return InlineKeyboardMarkup(
        inline_keyboard=[

            [
                InlineKeyboardButton(
                    text="🎂 Торты на заказ",
                    callback_data="menu|cakes"
                )
            ],

            [
                InlineKeyboardButton(
                    text="🧁 Капкейки",
                    callback_data="menu|cupcakes"
                )
            ],

            [
                InlineKeyboardButton(
                    text="🍰 Десерты",
                    callback_data="menu|desserts"
                )
            ],

            [
                InlineKeyboardButton(
                    text="🎁 Подарочные наборы",
                    callback_data="menu|gifts"
                )
            ],

            [
                InlineKeyboardButton(
                    text="📸 Наши работы",
                    callback_data="portfolio"
                )
            ],

            [
                InlineKeyboardButton(
                    text="👩‍🍳 Связаться с кондитером",
                    callback_data="contact_pastry"
                )
            ]

        ]
    )


def cakes_menu():

    return InlineKeyboardMarkup(
        inline_keyboard=[

            [
                InlineKeyboardButton(
                    text="🎂 Детские торты",
                    callback_data="cat|cakes_children"
                )
            ],

            [
                InlineKeyboardButton(
                    text="💍 Свадебные торты",
                    callback_data="cat|cakes_wedding"
                )
            ],

            [
                InlineKeyboardButton(
                    text="🎉 Праздничные торты",
                    callback_data="cat|cakes_holiday"
                )
            ],

            [
                InlineKeyboardButton(
                    text="🎨 Индивидуальный дизайн",
                    callback_data="cat|cakes_custom"
                )
            ],

            [
                InlineKeyboardButton(
                    text="🍰 Бенто-торты",
                    callback_data="cat|cakes_bento"
                )
            ],

            [
                InlineKeyboardButton(
                    text="👑 Премиум торты",
                    callback_data="cat|cakes_premium"
                )
            ],

            [
                InlineKeyboardButton(
                    text="🏠 Главное меню",
                    callback_data="home"
                )
            ]
        ]
    )


def cupcakes_menu():

    return InlineKeyboardMarkup(
        inline_keyboard=[

            [
                InlineKeyboardButton(
                    text="🧁 Классические",
                    callback_data="cat|cupcakes_classic"
                )
            ],

            [
                InlineKeyboardButton(
                    text="🍫 Шоколадные",
                    callback_data="cat|cupcakes_chocolate"
                )
            ],

            [
                InlineKeyboardButton(
                    text="🍓 Ягодные",
                    callback_data="cat|cupcakes_berry"
                )
            ],

            [
                InlineKeyboardButton(
                    text="🎉 Наборы капкейков",
                    callback_data="cat|cupcakes_sets"
                )
            ],

            [
                InlineKeyboardButton(
                    text="🏠 Главное меню",
                    callback_data="home"
                )
            ]
        ]
    )


def desserts_menu():

    return InlineKeyboardMarkup(
        inline_keyboard=[

            [
                InlineKeyboardButton(
                    text="🍰 Чизкейки",
                    callback_data="cat|desserts_cheesecake"
                )
            ],

            [
                InlineKeyboardButton(
                    text="🍫 Брауни",
                    callback_data="cat|desserts_brownie"
                )
            ],

            [
                InlineKeyboardButton(
                    text="🥤 Трайфлы",
                    callback_data="cat|desserts_trifle"
                )
            ],

            [
                InlineKeyboardButton(
                    text="🍭 Кейк-попсы",
                    callback_data="cat|desserts_cakepops"
                )
            ],

            [
                InlineKeyboardButton(
                    text="🌈 Макаронс",
                    callback_data="cat|desserts_macarons"
                )
            ],

            [
                InlineKeyboardButton(
                    text="🍪 Печенье ручной работы",
                    callback_data="cat|desserts_cookies"
                )
            ],

            [
                InlineKeyboardButton(
                    text="🏠 Главное меню",
                    callback_data="home"
                )
            ]
        ]
    )


def gifts_menu():

    return InlineKeyboardMarkup(
        inline_keyboard=[

            [
                InlineKeyboardButton(
                    text="🎁 Подарочные боксы",
                    callback_data="cat|gift_boxes"
                )
            ],

            [
                InlineKeyboardButton(
                    text="❤️ Романтические наборы",
                    callback_data="cat|gift_romantic"
                )
            ],

            [
                InlineKeyboardButton(
                    text="👶 Детские наборы",
                    callback_data="cat|gift_kids"
                )
            ],

            [
                InlineKeyboardButton(
                    text="🎂 Наборы на праздник",
                    callback_data="cat|gift_birthday"
                )
            ],

            [
                InlineKeyboardButton(
                    text="🏠 Главное меню",
                    callback_data="home"
                )
            ]
        ]
    )


def admin_menu():

    return InlineKeyboardMarkup(
        inline_keyboard=[

            [
                InlineKeyboardButton(
                    text="🛠 Управление каталогом",
                    callback_data="admin_catalog"
                )
            ],

            [
                InlineKeyboardButton(
                    text="➕ Добавить товар",
                    callback_data="admin_add"
                )
            ],

            [
                InlineKeyboardButton(
                    text="📸 Добавить работу",
                    callback_data="admin_add_portfolio"
                )
            ],

            [
                InlineKeyboardButton(
                    text="📦 Заявки",
                    callback_data="admin_orders"
                )
            ],

            [
                InlineKeyboardButton(
                    text="👥 Пользователи",
                    callback_data="admin_users"
                )
            ],

            [
                InlineKeyboardButton(
                    text="📊 Общая статистика",
                    callback_data="global_stats"
                )
            ],

            [
                InlineKeyboardButton(
                    text="💰 Изменить цену",
                    callback_data="admin_price"
                )
            ],

            [
                InlineKeyboardButton(
                    text="❌ Удалить товар",
                    callback_data="admin_delete"
                )
            ],

            [
                InlineKeyboardButton(
                    text="📢 Рассылка",
                    callback_data="admin_broadcast"
                )
            ],

            [
                InlineKeyboardButton(
                    text="✉️ Ответить клиенту",
                    callback_data="admin_reply"
                )
            ]

        ]
    )

# =====================================
# START
# =====================================
@dp.callback_query(
    F.data == "global_stats"
)
async def global_stats(
    callback: CallbackQuery
):

    cursor.execute("""
    SELECT city, COUNT(*)
    FROM users
    GROUP BY city
    ORDER BY COUNT(*) DESC
    """)

    rows = cursor.fetchall()

    cursor.execute(
        "SELECT COUNT(*) FROM users"
    )

    total_users = cursor.fetchone()[0]

    text = "📊 ОБЩАЯ СТАТИСТИКА\n\n"

    for city, count in rows:
        text += f"🏙 {city}: {count}\n"

    text += f"\n👥 Всего пользователей: {total_users}"

    await callback.message.answer(text)

    await callback.answer()
@dp.message(Command("start"))
async def start_handler(message: Message):

    print(
        "START:",
        message.bot.id
    )

    city = BOT_CITIES.get(
        str(message.bot.id),
        "Неизвестно"
    )

    cursor.execute(
        "SELECT user_id FROM users WHERE user_id=?",
        (message.from_user.id,)
    )

    user = cursor.fetchone()

    is_new = user is None

    if is_new:

        print(
            f"Пользователь записан в город: {city}"
        )

        cursor.execute("""
        INSERT INTO users (
            user_id,
            city,
            first_name,
            username
        )
        VALUES (?, ?, ?, ?)
        """, (
            message.from_user.id,
            city,
            message.from_user.first_name,
            message.from_user.username
        ))

        conn.commit()

        status = "🆕 Новый пользователь"

    else:

        status = "♻️ Повторный запуск"

    cursor.execute(
        "SELECT COUNT(*) FROM users"
    )

    total_users = cursor.fetchone()[0]

    await message.bot.send_message(
        ADMIN_ID,
        f"{status}\n\n"
        f"👤 Имя: {message.from_user.first_name}\n"
        f"📛 Username: @{message.from_user.username if message.from_user.username else 'нет'}\n"
        f"🆔 ID: {message.from_user.id}\n"
        f"🏙 Город: {city}\n"
        f"👥 Всего пользователей: {total_users}"
    )

    await message.answer(
        "🎂 Добро пожаловать в кондитерскую!\n\n"
        "Выберите интересующий раздел:",
        reply_markup=main_menu()
    )
@dp.message(Command("admin"))
async def admin_panel(message: Message):

    if message.from_user.id != ADMIN_ID:

        await message.answer(
            "⛔ Нет доступа"
        )

        return

    await message.answer(
        "🔐 Админ панель",
        reply_markup=admin_menu()
    )
@dp.callback_query(F.data == "admin_catalog")
async def admin_catalog(callback: CallbackQuery):

    await callback.message.answer(
        "Выберите раздел:",
        reply_markup=main_menu()
    )

    await callback.answer()
# =====================================
# КЛАВИАТУРА ТОВАРА
# =====================================

def product_keyboard(category, index, total, is_admin=False):

    buttons = []

    row = []

    if index > 0:
        row.append(
            InlineKeyboardButton(
                text="⬅️",
                callback_data=f"view|{category}|{index-1}"
            )
        )

    row.append(
        InlineKeyboardButton(
            text="🛒 Заказать",
            callback_data=f"order|{category}|{index}"
        )
    )

    if index < total - 1:
        row.append(
            InlineKeyboardButton(
                text="➡️",
                callback_data=f"view|{category}|{index+1}"
            )
        )

    buttons.append(row)

    if is_admin:

        buttons.append([
            InlineKeyboardButton(
                text="✏️ Изменить",
                callback_data=f"edit|{category}|{index}"
            )
        ])

        buttons.append([
            InlineKeyboardButton(
                text="🗑 Удалить",
                callback_data=f"delete|{category}|{index}"
            )
        ])

    buttons.append([
        InlineKeyboardButton(
            text="🏠 Главное меню",
            callback_data="home"
        )
    ])

    return InlineKeyboardMarkup(
        inline_keyboard=buttons
    )

# =====================================
# ГЛАВНОЕ МЕНЮ
# =====================================

@dp.callback_query(F.data == "home")
async def home(callback: CallbackQuery):

    await callback.message.answer(
        "🏠 Главное меню",
        reply_markup=main_menu()
    )

    await callback.answer()


# =====================================
# ОТКРЫТИЕ РАЗДЕЛОВ
# =====================================

@dp.callback_query(F.data == "menu|cakes")
async def open_cakes(callback: CallbackQuery):

    await callback.message.answer(
        "🎂 Выберите категорию:",
        reply_markup=cakes_menu()
    )

    await callback.answer()


@dp.callback_query(F.data == "menu|cupcakes")
async def open_cupcakes(callback: CallbackQuery):

    await callback.message.answer(
        "🧁 Выберите категорию:",
        reply_markup=cupcakes_menu()
    )

    await callback.answer()


@dp.callback_query(F.data == "menu|desserts")
async def open_desserts(callback: CallbackQuery):

    await callback.message.answer(
        "🍰 Выберите категорию:",
        reply_markup=desserts_menu()
    )

    await callback.answer()


@dp.callback_query(F.data == "menu|gifts")
async def open_gifts(callback: CallbackQuery):

    await callback.message.answer(
        "🎁 Выберите категорию:",
        reply_markup=gifts_menu()
    )

    await callback.answer()


# =====================================
# КАТЕГОРИИ ТОВАРОВ
# =====================================

@dp.callback_query(lambda c: c.data.startswith("cat|"))
async def open_category(callback: CallbackQuery):

    _, category = callback.data.split("|")

    catalog = load_catalog()
    products = catalog[category]

    if not products:

        await callback.message.answer(
            "😔 Пока товаров нет"
        )

        await callback.answer()
        return

    product = products[0]

    photo_path = os.path.join(
        PHOTOS_DIR,
        product["photo"]
    )

    caption = (
        f"🍰 {product['name']}\n\n"
        f"💰 Цена: {product['price']} "
    )

    is_admin = callback.from_user.id == ADMIN_ID

    await callback.message.answer_photo(
        FSInputFile(photo_path),
        caption=caption,
        reply_markup=product_keyboard(
            category,
            0,
            len(products),
            is_admin
        )
    )

    await callback.answer()
# =====================================
# ЛИСТАНИЕ
# =====================================

@dp.callback_query(
    lambda c: c.data.startswith("view|")
)
async def view_product(callback: CallbackQuery):

    _, category, index = callback.data.split("|")

    index = int(index)

    catalog = load_catalog()
    products = catalog[category]

    product = products[index]

    photo_path = os.path.join(
        PHOTOS_DIR,
        product["photo"]
    )

    caption = (
        f"🍰 {product['name']}\n\n"
        f"💰 Цена: {product['price']} "
    )

    media = types.InputMediaPhoto(
        media=FSInputFile(photo_path),
        caption=caption
    )

    is_admin = callback.from_user.id == ADMIN_ID

    await callback.message.edit_media(
        media=media,
        reply_markup=product_keyboard(
            category,
            index,
            len(products),
            is_admin
        )
    )

    await callback.answer()

# =====================================
# НАШИ РАБОТЫ
# =====================================

@dp.callback_query(F.data == "portfolio")
async def open_portfolio(
    callback: CallbackQuery
):

    catalog = load_catalog()

    works = catalog["portfolio"]

    if not works:

        await callback.message.answer(
            "📸 Работы пока не добавлены"
        )

        await callback.answer()
        return

    first = works[0]

    photo_path = os.path.join(
        PORTFOLIO_DIR,
        first["photo"]
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="➡️",
                    callback_data="portfolio_view|1"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🏠 Главное меню",
                    callback_data="home"
                )
            ]
        ]
    )

    await callback.message.answer_photo(
        FSInputFile(photo_path),
        caption="📸 Наши работы",
        reply_markup=keyboard
    )

    await callback.answer()


@dp.callback_query(
    lambda c: c.data.startswith(
        "portfolio_view|"
    )
)
async def portfolio_view(
    callback: CallbackQuery
):

    index = int(
        callback.data.split("|")[1]
    )

    catalog = load_catalog()

    works = catalog["portfolio"]

    if index >= len(works):
        index = 0

    photo_path = os.path.join(
        PORTFOLIO_DIR,
        works[index]["photo"]
    )

    next_index = index + 1

    if next_index >= len(works):
        next_index = 0

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="➡️",
                    callback_data=f"portfolio_view|{next_index}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🏠 Главное меню",
                    callback_data="home"
                )
            ]
        ]
    )

    media = types.InputMediaPhoto(
        media=FSInputFile(photo_path),
        caption="📸 Наши работы"
    )

    await callback.message.edit_media(
        media=media,
        reply_markup=keyboard
    )

    await callback.answer()
# =====================================
# ЗАКАЗ ИЗ КАТАЛОГА
# =====================================

@dp.callback_query(
    lambda c: c.data.startswith("order|")
)
async def make_order(callback: CallbackQuery):

    _, category, index = callback.data.split("|")

    index = int(index)

    catalog = load_catalog()

    product = catalog[category][index]

    user = callback.from_user

    orders = load_orders()

    orders.append({

        "user_id": user.id,
        "name": user.first_name,
        "username": user.username,

        "product": product["name"],
        "price": product["price"]

    })

    save_orders(orders)

username = (
    f"@{user.username}"
    if user.username
    else "нет"
)

text = (
    "🛒 НОВЫЙ ЗАКАЗ\n\n"

    f"👤 Имя: {user.first_name}\n"
    f"🔗 Username: {username}\n"
    f"🆔 ID: {user.id}\n\n"

    f"🎂 Товар: {product['name']}\n"
    f"💰 Цена: {product['price']}"
)

await callback.bot.send_message(
    ADMIN_ID,
    text
)

await callback.message.answer(
    "✅ Заявка отправлена.\n\n"
    "Мы скоро свяжемся с вами."
)

await callback.answer()

# =====================================
# СВЯЗЬ С КОНДИТЕРОМ
# =====================================

@dp.callback_query(
    F.data == "contact_pastry"
)
async def contact_pastry(
    callback: CallbackQuery,
    state: FSMContext
):

    await callback.message.answer(
        "🎂 Что хотите заказать?\n\n"
        "Например:\n"
        "Торт, капкейки, набор десертов..."
    )

    await state.set_state(
        Consultation.product_type
    )

    await callback.answer()


@dp.message(
    Consultation.product_type
)
async def consult_product(
    message: Message,
    state: FSMContext
):

    await state.update_data(
        product_type=message.text
    )

    await message.answer(
        "📅 На какую дату нужен заказ?"
    )

    await state.set_state(
        Consultation.date
    )


@dp.message(
    Consultation.date
)
async def consult_date(
    message: Message,
    state: FSMContext
):

    await state.update_data(
        date=message.text
    )

    await message.answer(
        "👥 На сколько человек?"
    )

    await state.set_state(
        Consultation.guests
    )


@dp.message(
    Consultation.guests
)
async def consult_guests(
    message: Message,
    state: FSMContext
):

    await state.update_data(
        guests=message.text
    )

    await message.answer(
        "📝 Опишите пожелания.\n\n"
        "Дизайн, вес, начинка, цвет и т.д."
    )

    await state.set_state(
        Consultation.wishes
    )


@dp.message(
    Consultation.wishes
)
async def consult_finish(
    message: Message,
    state: FSMContext
):

    data = await state.get_data()

    username = (
        f"@{message.from_user.username}"
        if message.from_user.username
        else "нет"
    )

    text = (
        "🔔 НОВАЯ КОНСУЛЬТАЦИЯ\n\n"

        f"👤 Клиент: {message.from_user.first_name}\n"
        f"🔗 Username: {username}\n"
        f"🆔 ID: {message.from_user.id}\n\n"

        f"🎂 Заказ: {data['product_type']}\n"
        f"📅 Дата: {data['date']}\n"
        f"👥 Гостей: {data['guests']}\n\n"

        f"📝 Пожелания:\n"
        f"{message.text}"
    )

    await message.bot.send_message(
        ADMIN_ID,
        text
    )

    await message.answer(
        "✅ Заявка отправлена кондитеру.\n\n"
        f"Для быстрой связи:\n{CONDITER_LINK}"
    )

    await state.clear()
# =====================================
# ДОБАВЛЕНИЕ ТОВАРОВ
# =====================================


@dp.callback_query(F.data == "admin_add")
async def add_product_start(
    callback: CallbackQuery,
    state: FSMContext
):

    if callback.from_user.id != ADMIN_ID:
        return

    catalog = load_catalog()

    categories = [
        k for k in catalog.keys()
        if k != "portfolio"
    ]

    text = "➕ Выберите категорию:\n\n"

    category_map = {}

    for i, cat in enumerate(categories, start=1):

        category_map[str(i)] = cat

        text += f"{i} — {CATEGORY_NAMES.get(cat, cat)}\n"

    await state.update_data(
        category_map=category_map
    )

    await callback.message.answer(text)

    await state.set_state(AddProduct.category)

    await callback.answer()


@dp.message(AddProduct.category)
async def add_product_category(
    message: Message,
    state: FSMContext
):

    data = await state.get_data()

    category_map = data["category_map"]

    if message.text not in category_map:

        await message.answer("❌ Введите номер из списка")
        return

    category = category_map[message.text]

    await state.update_data(category=category)

    await message.answer("Введите название товара")

    await state.set_state(AddProduct.name)

@dp.message(AddProduct.name)
async def add_product_name(
    message: Message,
    state: FSMContext
):

    await state.update_data(
        name=message.text
    )

    await message.answer(
        "Введите цену"
    )

    await state.set_state(
        AddProduct.price
    )


@dp.message(AddProduct.price)
async def add_product_price(
    message: Message,
    state: FSMContext
):

    await state.update_data(
        price=message.text
    )

    await message.answer(
        "Отправьте фото"
    )

    await state.set_state(
        AddProduct.photo
    )


@dp.message(AddProduct.photo)
async def add_product_photo(
    message: Message,
    state: FSMContext
):

    if not message.photo:
        return

    data = await state.get_data()

    catalog = load_catalog()

    file = await message.bot.get_file(
    message.photo[-1].file_id
    )

    import uuid

    filename = f"{uuid.uuid4().hex}.jpg"

    filepath = os.path.join(
        PHOTOS_DIR,
        filename
    )

    await message.bot.download_file(
    file.file_path,
    filepath
    )

    catalog[data["category"]].append({

        "name": data["name"],
        "price": data["price"],
        "photo": filename

    })

    save_catalog(catalog)

    await message.answer(
        "✅ Товар добавлен"
    )

    await state.clear()


# =====================================
# ДОБАВЛЕНИЕ В ПОРТФОЛИО
# =====================================

@dp.callback_query(F.data == "admin_add_portfolio")
async def add_portfolio_start(callback: CallbackQuery, state: FSMContext):

    if callback.from_user.id != ADMIN_ID:
        return

    await callback.message.answer("📸 Отправьте фото работы")

    await state.set_state(AddPortfolio.photo)

    await callback.answer()
@dp.message(AddPortfolio.photo)
async def portfolio_upload(message: Message, state: FSMContext):

    if message.from_user.id != ADMIN_ID:
        return

    if not message.photo:
        return

    file = await bot.get_file(message.photo[-1].file_id)

    filename = f"work_{message.message_id}.jpg"
    filepath = os.path.join(PORTFOLIO_DIR, filename)

    await bot.download_file(file.file_path, filepath)

    catalog = load_catalog()
    catalog["portfolio"].append({"photo": filename})
    save_catalog(catalog)

    await message.answer("✅ Работа добавлена")

    await state.clear()

# =====================================
# ЗАЯВКИ
# =====================================

@dp.callback_query(
    F.data == "admin_orders"
)
async def admin_orders(
    callback: CallbackQuery
):

    orders = load_orders()

    if not orders:

        await callback.message.answer(
            "Заявок нет"
        )

        return

    text = "📦 ЗАЯВКИ\n\n"

    for order in orders:

        text += (
            f"👤 {order['name']}\n"
            f"🆔 {order['user_id']}\n"
            f"🎂 {order['product']}\n"
            f"💰 {order['price']} ₽\n\n"
        )

    await callback.message.answer(text)


# =====================================
# СТАТИСТИКА
# =====================================

@dp.callback_query(F.data == "admin_users")
async def admin_users(callback: CallbackQuery):

    city = BOT_CITIES.get(
        str(callback.bot.id),
        "Неизвестно"
    )

    cursor.execute(
        "SELECT COUNT(*) FROM users WHERE city=?",
        (city,)
    )

    users_count = cursor.fetchone()[0]

    await callback.message.answer(
        f"📊 Статистика города\n\n"
        f"🏙 Город: {city}\n"
        f"👥 Пользователей: {users_count}"
    )

# =====================================
# РАССЫЛКА
# =====================================

@dp.callback_query(
    F.data == "admin_broadcast"
)
async def broadcast_start(
    callback: CallbackQuery,
    state: FSMContext
):

    await callback.message.answer(
    "Введите текст рассылки"
    )

    await state.set_state(
        Broadcast.text
    )


@dp.message(Broadcast.text)
async def broadcast_send(
    message: Message,
    state: FSMContext
):

    city = BOT_CITIES.get(
        str(message.bot.id)
    )

    cursor.execute(
        """
        SELECT user_id
        FROM users
        WHERE city=?
        """,
        (city,)
    )

    users = cursor.fetchall()

    sent = 0

    for user in users:

        try:

            await message.bot.send_message(
                user[0],
                message.text
            )

            sent += 1

        except:
            pass

    await message.answer(
        f"✅ Отправлено: {sent}"
    )

    await state.clear()
# =====================================
# ОТВЕТ ПОЛЬЗОВАТЕЛЮ
# =====================================

@dp.callback_query(
    F.data == "admin_reply"
)
async def reply_start(
    callback: CallbackQuery,
    state: FSMContext
):

    await callback.message.answer(
        "Введите ID пользователя"
    )

    await state.set_state(
        ReplyUser.user_id
    )


@dp.message(ReplyUser.user_id)
async def reply_user_id(
    message: Message,
    state: FSMContext
):

    await state.update_data(
        user_id=message.text
    )

    await message.answer(
        "Введите сообщение"
    )

    await state.set_state(
        ReplyUser.text
    )


@dp.message(ReplyUser.text)
async def reply_send(
    message: Message,
    state: FSMContext
):

    data = await state.get_data()

    try:

        await message.bot.send_message(
            int(data["user_id"]),
            f"👩‍🍳 Сообщение кондитера:\n\n{message.text}"
        )

        await message.answer(
            "✅ Отправлено"
        )

    except:

        await message.answer(
            "❌ Ошибка"
        )

    await state.clear()
# =====================================
# УДАЛЕНИЕ ТОВАРА
# =====================================

@dp.callback_query(F.data == "admin_delete")
async def delete_product_start(
    callback: CallbackQuery,
    state: FSMContext
):

    catalog = load_catalog()

    products_map = {}

    text = "❌ Удаление товара\n\n"

    number = 1

    for category, products in catalog.items():

        if category == "portfolio":
            continue

        for index, product in enumerate(products):

            products_map[str(number)] = {
                "category": category,
                "index": index
            }

            text += (
                f"{number} — "
                f"{product['name']} "
                f"({product['price']} ₽)\n"
            )

            number += 1

    if number == 1:

        await callback.message.answer(
            "Товаров нет"
        )
        return

    await state.update_data(
        delete_map=products_map
    )

    await callback.message.answer(
        text + "\n\nВведите номер товара для удаления:"
    )

    await state.set_state(
        DeleteProduct.product
    )

    await callback.answer()


@dp.message(DeleteProduct.product)
async def delete_product_finish(
    message: Message,
    state: FSMContext
):

    data = await state.get_data()

    delete_map = data["delete_map"]

    if message.text not in delete_map:

        await message.answer(
            "❌ Такого номера нет"
        )
        return

    selected = delete_map[message.text]

    catalog = load_catalog()

    category = selected["category"]
    index = selected["index"]

    product = catalog[category][index]

    product_name = product["name"]

    try:

        photo_path = os.path.join(
            PHOTOS_DIR,
            product["photo"]
        )

        if os.path.exists(photo_path):
            os.remove(photo_path)

    except:
        pass

    del catalog[category][index]

    save_catalog(catalog)

    await message.answer(
        f"✅ Товар удалён:\n{product_name}"
    )

    await state.clear()
# =====================================
# ИЗМЕНЕНИЕ ЦЕНЫ
# =====================================

@dp.callback_query(F.data == "admin_price")
async def change_price_start(
    callback: CallbackQuery,
    state: FSMContext
):

    catalog = load_catalog()

    products_map = {}

    text = "💰 Изменение цены\n\n"

    number = 1

    for category, products in catalog.items():

        if category == "portfolio":
            continue

        for index, product in enumerate(products):

            products_map[str(number)] = {
                "category": category,
                "index": index
            }

            text += (
                f"{number} — "
                f"{product['name']} "
                f"({product['price']} ₽)\n"
            )

            number += 1

    if number == 1:

        await callback.message.answer(
            "Товаров нет"
        )
        return

    await state.update_data(
        products_map=products_map
    )

    await callback.message.answer(
        text + "\n\nВведите номер товара:"
    )

    await state.set_state(
        ChangePrice.product
    )


@dp.message(ChangePrice.product)
async def change_price_product(
    message: Message,
    state: FSMContext
):

    data = await state.get_data()

    products_map = data["products_map"]

    if message.text not in products_map:

        await message.answer(
            "❌ Такого номера нет"
        )
        return

    await state.update_data(
        selected=products_map[
            message.text
        ]
    )

    await message.answer(
        "Введите новую цену:"
    )

    await state.set_state(
        ChangePrice.price
    )


@dp.message(ChangePrice.price)
async def change_price_finish(
    message: Message,
    state: FSMContext
):

    data = await state.get_data()

    selected = data["selected"]

    catalog = load_catalog()

    category = selected["category"]
    index = selected["index"]

    catalog[category][index]["price"] = (
        message.text
    )

    product_name = catalog[
        category
    ][
        index
    ]["name"]

    save_catalog(catalog)

    await message.answer(
        f"✅ Цена товара\n"
        f"«{product_name}»\n"
        f"изменена на {message.text} "
    )

    await state.clear()
# =====================================
# УДАЛЕНИЕ ИЗ КАРТОЧКИ ТОВАРА
# =====================================

@dp.callback_query(lambda c: c.data.startswith("delete|"))
async def delete_product_card(callback: CallbackQuery):

    if callback.from_user.id != ADMIN_ID:
        return

    _, category, index = callback.data.split("|")

    index = int(index)

    catalog = load_catalog()

    product = catalog[category][index]

    try:
        photo_path = os.path.join(
            PHOTOS_DIR,
            product["photo"]
        )

        if os.path.exists(photo_path):
            os.remove(photo_path)

    except:
        pass

    product_name = product["name"]

    del catalog[category][index]

    save_catalog(catalog)

    await callback.message.answer(
        f"✅ Товар удалён:\n{product_name}"
    )

    await callback.answer()
# =====================================
# ИЗМЕНЕНИЕ ЦЕНЫ ИЗ КАРТОЧКИ
# =====================================

@dp.callback_query(lambda c: c.data.startswith("edit|"))
async def edit_product_card(
    callback: CallbackQuery,
    state: FSMContext
):

    if callback.from_user.id != ADMIN_ID:
        return

    _, category, index = callback.data.split("|")

    await state.update_data(
        category=category,
        index=int(index)
    )

    await callback.message.answer(
        "💰 Введите новую цену:"
    )

    await state.set_state(
        EditCardPrice.price
    )

    await callback.answer()


@dp.message(EditCardPrice.price)
async def save_card_price(
    message: Message,
    state: FSMContext
):

    data = await state.get_data()

    category = data["category"]
    index = data["index"]

    catalog = load_catalog()

    catalog[category][index]["price"] = message.text

    product_name = catalog[category][index]["name"]

    save_catalog(catalog)

    await message.answer(
        f"✅ Цена товара\n"
        f"«{product_name}»\n"
        f"изменена на {message.text} ₽"
    )

    await state.clear()

# =====================================
# ЗАПУСК
# =====================================

async def run_bot(token, city):

    local_bot = Bot(token=token)

    local_dp = deepcopy(dp)

    me = await local_bot.get_me()

    print(f"БОТ ЗАПУЩЕН: {city} | @{me.username}")

    await local_dp.start_polling(local_bot)


async def main():

    with open("bots.json", "r", encoding="utf-8") as f:
        bots_data = json.load(f)

    global BOT_CITIES

    BOT_CITIES = {}

    for bot_name, data in bots_data.items():

        token = data["token"]

        bot_id = token.split(":")[0]

        BOT_CITIES[bot_id] = data["city"]

    tasks = []

    for bot_name, data in bots_data.items():

        tasks.append(
            asyncio.create_task(
                run_bot(
                    data["token"],
                    data["city"]
                )
            )
        )

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())