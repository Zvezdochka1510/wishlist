import asyncio
import sqlite3

from aiogram import Bot, Dispatcher, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Замените токен на ваш
API_TOKEN = '7405564479:AAFF1Z8iNYSxqmtedDcjMYay8Xp74C8GFeg'

# Создаем объекты Bot и Dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot=bot, storage=MemoryStorage())


# Подключение к базе данных
db_queue = asyncio.Queue()
authorized_users = [2045383874, 998211350]  # Замените на список разрешенных пользователей

def connect_db():
    conn = sqlite3.connect('wishlist.db')
    cursor = conn.cursor()
    return cursor

async def execute_query(query, params=None):
    cursor = connect_db()
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        conn.commit()
        result = cursor.fetchall()
        return result
    except sqlite3.Error as error:
        print(f"Ошибка при выполнении запроса: {error}")
    finally:
        conn.close()

# Создание клавиатур
wishlist_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
wishlist_keyboard.add(KeyboardButton("Настины хотелки"), KeyboardButton("Данины хотелки"))
wishlist_keyboard.add(KeyboardButton("Добавить новую хотелку"), KeyboardButton("Удалить хотелку"))

# Создание состояний для FSM
class WishListState(StatesGroup):
    adding_item = State()
    deleting_item = State()

# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    if message.from_user.id not in authorized_users:
        await message.reply("У вас нет доступа к этому боту.")
        return
    await message.reply("Привет! Я бот для хотелок. Что вы хотите сделать?", reply_markup=wishlist_keyboard)

# Обработчик нажатия на кнопку "Настины хотелки"
@dp.message_handler(text="Настины хотелки")
async def show_nastia_wishlist(message: types.Message):
    await db_queue.put((execute_query, ("SELECT url FROM wishlist WHERE user = 'Настя'", )))
    await db_queue.join()  # Ожидание завершения задачи
    wishlist_items = await execute_query("SELECT url FROM wishlist WHERE user = 'Настя'")
    if wishlist_items:
        wishlist_str = 'n'.join([item[0] for item in wishlist_items])
        await message.reply(f"Вот хотелки Насти:n{wishlist_str}")
    else:
        await message.reply("У Насти пока нет хотелок.")

        # Обработчик нажатия на кнопку "Данины хотелки"

    @dp.message_handler(text="Данины хотелки")
    async def show_danya_wishlist(message: types.Message):
        await db_queue.put((execute_query, ("SELECT url FROM wishlist WHERE user = 'Даниил'",)))
        await db_queue.join()  # Ожидание завершения задачи
        wishlist_items = await execute_query("SELECT url FROM wishlist WHERE user = 'Даниил'")
        if wishlist_items:
            wishlist_str = 'n'.join([item[0] for item in wishlist_items])
            await message.reply(f"Вот хотелки Дани:n{wishlist_str}")
        else:
            await message.reply("У Дани пока нет хотелок.")

    # Обработчик нажатия на кнопку "Добавить новую хотелку"
    @dp.message_handler(text="Добавить новую хотелку")
    async def add_wishlist_item(message: types.Message):
        if message.from_user.id not in authorized_users:
            await message.reply("У вас нет доступа к добавлению хотелок.")
            return

        await message.reply("Отправьте ссылку на хотелку:")
        await WishListState.adding_item.set()

    # Обработчик ввода ссылки на хотелку
    @dp.message_handler(state=WishListState.adding_item)
    async def process_wishlist_item(message: types.Message, state: FSMContext):
        if not message.text.startswith('http'):
            await message.reply("Неправильный формат ссылки. Попробуйте снова.")
            return

        user = message.from_user.first_name
        url = message.text
        await db_queue.put((execute_query, ("INSERT INTO wishlist (user, url) VALUES (?, ?)", (user, url))))
        await db_queue.join()
        await message.reply("Хотелка добавлена!")
        await state.finish()

    # Обработчик нажатия на кнопку "Удалить хотелку"
    @dp.message_handler(text="Удалить хотелку")
    async def delete_wishlist_item(message: types.Message):
        if message.from_user.id not in authorized_users:
            await message.reply("У вас нет доступа к удалению хотелок.")
            return

        await message.reply("Введите ссылку на хотелку, которую хотите удалить:")
        await WishListState.deleting_item.set()

    # Обработчик ввода ссылки на удаляемую хотелку
    @dp.message_handler(state=WishListState.deleting_item)
    async def process_delete_wishlist_item(message: types.Message, state: FSMContext):
        url = message.text
        user = message.from_user.first_name
        await db_queue.put((execute_query, ("DELETE FROM wishlist WHERE url = ? AND user = ?", (url, user))))
        await db_queue.join()
        await message.reply("Хотелка удалена!")
        await state.finish()

    # Запускаем бота
    if __name__ == '__main__':
        executor.start_polling(dp, skip_updates=True)
