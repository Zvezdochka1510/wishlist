import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.utils.executor import start_polling, start_webhook
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

import sqlite3

# Замените токен на ваш
API_TOKEN = '7405564479:AAFF1Z8iNYSxqmtedDcjMYay8Xp74C8GFeg'

# Создаем объекты Bot и Dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# Подключение к базе данных
db_conn = sqlite3.connect('wishlist.db')
db_cursor = db_conn.cursor()

# Создаем таблицу, если ее нет
db_cursor.execute('''
    CREATE TABLE IF NOT EXISTS wishlist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        url TEXT
    )
''')
db_conn.commit()

# Создаем клавиатур
wishlist_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
wishlist_keyboard.add(KeyboardButton("Настины хотелки"), KeyboardButton("Данины хотелки"))
wishlist_keyboard.add(KeyboardButton("Добавить хотелку"), KeyboardButton("Удалить хотелку"))

# Создание состояний для FSM
class WishListState(StatesGroup):
    adding_item = State()
    deleting_item = State()

# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Привет! Я бот для хотелок. Что вы хотите сделать?", reply_markup=wishlist_keyboard)

# Обработчик нажатия на кнопку "Настины хотелки"
@dp.message_handler(text="Настины хотелки")
async def show_nastia_wishlist(message: types.Message):
    wishlist_items = db_cursor.execute("SELECT url FROM wishlist WHERE user_id = 2045383874").fetchall()
    if wishlist_items:
        wishlist_str = "n".join([item[0] for item in wishlist_items])
        await message.reply(f"Вот хотелки Насти:n{wishlist_str}")
    else:
        await message.reply("У Насти пока нет хотелок.")

# Обработчик нажатия на кнопку "Данины хотелки"
@dp.message_handler(text="Данины хотелки")
async def show_danya_wishlist(message: types.Message):
    wishlist_items = db_cursor.execute("SELECT url FROM wishlist WHERE user_id = 998211350").fetchall()
    if wishlist_items:
        wishlist_str = "n".join([item[0] for item in wishlist_items])
        await message.reply(f"Вот хотелки Дани:n{wishlist_str}")
    else:
        await message.reply("У Дани пока нет хотелок.")

# Обработчик нажатия на кнопку "Добавить новую хотелку"
@dp.message_handler(text="Добавить хотелку")
async def add_wishlist_item(message: types.Message):
    await message.reply("Отправьте ссылку на хотелку:")
    await WishListState.adding_item.set()

# Обработчик ввода ссылки на хотелку
@dp.message_handler(state=WishListState.adding_item)
async def process_wishlist_item(message: types.Message, state: FSMContext):
    url = message.text
    if not url.startswith('http'):
        await message.reply("Неправильный формат ссылки. Попробуйте снова.")
        return

    user_id = message.from_user.id  # Получаем ID пользователя

    db_cursor.execute("INSERT INTO wishlist (user_id, url) VALUES (?, ?)", (user_id, url))
    db_conn.commit()

    await message.reply("Хотелка добавлена!")
    await state.finish()

# Обработчик нажатия на кнопку "Удалить хотелку"
@dp.message_handler(text="Удалить хотелку")
async def delete_wishlist_item(message: types.Message):
    await message.reply("Введите ссылку на хотелку, которую хотите удалить:")
    await WishListState.deleting_item.set()

# Обработчик ввода ссылки на удаляемую хотелку
@dp.message_handler(state=WishListState.deleting_item)
async def process_delete_wishlist_item(message: types.Message, state: FSMContext):
    url = message.text
    user_id = message.from_user.id  # Получаем ID пользователя

    db_cursor.execute("DELETE FROM wishlist WHERE url = ? AND user_id = ?", (url, user_id))
    db_conn.commit()

    await message.reply("Хотелка удалена!")
    await state.finish()

if __name__ == '__main__':
    start_polling(dp, skip_updates=True)
