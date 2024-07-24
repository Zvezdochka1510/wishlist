import telebot
from telebot import types
import sqlite3
import threading
import queue

# Создаем экземпляр бота
bot = telebot.TeleBot("7405564479:AAFF1Z8iNYSxqmtedDcjMYay8Xp74C8GFeg")

def init():
    conn = sqlite3.connect('wishlist.db')
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wishlist (
            id INTEGER PRIMARY KEY,
            user TEXT,
            url TEXT
        )
    """)
    conn.commit()

def connect_db():
    # Создаем подключение к базе данных
    conn = sqlite3.connect('wishlist.db')

    # Создаем таблицу wishlist, если она еще не существует
    cursor = conn.cursor()
    return cursor




# Добавляем столбец url в таблицу wishlist, если его еще нет
try:
    cursor = connect_db()
    cursor.execute("""
        ALTER TABLE wishlist ADD COLUMN IF NOT EXISTS url TEXT
    """)
except sqlite3.OperationalError:
    # Обработка ошибки, если таблица wishlist не существует
    pass

# Список пользователей, которые могут использовать бота
authorized_users = [2045383874, 998211350]

# Создаем очередь для задач базы данных
db_queue = queue.Queue()

# Функция для обработки задач базы данных
def process_db_tasks():
    while True:
        task, args = db_queue.get()
        try:
            task(*args)  # Выполняем задачу
        except Exception as e:
            # Обрабатываем исключения здесь
            print(f"Error in database task: {e}")
        finally:
            db_queue.task_done()

# Запускаем поток для обработки задач базы данных
db_thread = threading.Thread(target=process_db_tasks)
db_thread.daemon = True  # Делаем его потоком-демоном, чтобы он не блокировал завершение
db_thread.start()

# Функция для выполнения запросов в базе данных
def execute_query(query, args=None):
    conn = sqlite3.connect('wishlist.db')
    cursor = connect_db()
    with conn:
        if args:
            cursor.execute(query, args)
        else:
            cursor.execute(query)
        return cursor.fetchall()

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    # Проверяем, авторизован ли пользователь
    if message.from_user.id not in authorized_users:
        bot.send_message(message.chat.id, "У вас нет доступа к этому боту.")
        return

    # Выводим приветствие и меню
    markup = types.ReplyKeyboardMarkup(row_width=2)
    item1 = types.KeyboardButton("Настины хотелки")
    item2 = types.KeyboardButton("Данины хотелки")
    item3 = types.KeyboardButton("Добавить новую хотелку")
    item4 = types.KeyboardButton("Удалить хотелку")
    markup.add(item1, item2, item3, item4)

    bot.send_message(message.chat.id, "Привет! Выберите действие:", reply_markup=markup)

# Обработчик нажатия на кнопку "Настины хотелки"
@bot.message_handler(func=lambda message: message.text == "Настины хотелки")
def show_nastia_wishlist(message):
    # conn = sqlite3.connect('wishlist.db')
    cursor = connect_db()
    db_queue.put((execute_query, ("SELECT url FROM wishlist WHERE user = 'Настя'", )))
    db_queue.join()  # Ожидание завершения задачи
    wishlist_items = execute_query("SELECT url FROM wishlist WHERE user = 'Настя'")
    if wishlist_items:
        wishlist_str = '\n'.join([item[0] for item in wishlist_items])
        bot.send_message(message.chat.id, f"Вот хотелки Насти:\n{wishlist_str}")
    else:
        bot.send_message(message.chat.id, "У Насти пока нет хотелок.")

# Обработчик нажатия на кнопку "Данины хотелки"
@bot.message_handler(func=lambda message: message.text == "Данины хотелки")
def show_danya_wishlist(message):
    # conn = sqlite3.connect('wishlist.db')
    cursor = connect_db()
    db_queue.put((execute_query, ("SELECT url FROM wishlist WHERE user = 'Даниил'", )))
    db_queue.join()  # Ожидание завершения задачи
    wishlist_items = execute_query("SELECT url FROM wishlist WHERE user = 'Даниил'")
    if wishlist_items:
        wishlist_str = '\n'.join([item[0] for item in wishlist_items])
        bot.send_message(message.chat.id, f"Вот хотелки Дани:\n{wishlist_str}")
    else:
        bot.send_message(message.chat.id, "У Дани пока нет хотелок.")

# Обработчик нажатия на кнопку "Добавить новую хотелку"
@bot.message_handler(func=lambda message: message.text == "Добавить новую хотелку")
def add_wishlist_item(message):
    if message.from_user.id not in authorized_users:
        bot.send_message(message.chat.id, "У вас нет доступа к добавлению хотелок.")
        return

    # Запрашиваем ссылку на хотелку
    bot.send_message(message.chat.id, "Отправьте ссылку на хотелку:")
    bot.register_next_step_handler(message, process_wishlist_item)

def process_wishlist_item(message):
    # Проверяем, что ссылка валидная
    if not message.text.startswith('http'):
        bot.send_message(message.chat.id, "Неправильный формат ссылки. Попробуйте снова.")
        bot.register_next_step_handler(message, process_wishlist_item)
        return

    # Добавляем ссылку в базу данных
    user = message.from_user.first_name  # Получаем имя пользователя из объекта message
    url = message.text
    db_queue.put((execute_query, ("INSERT INTO wishlist (user, url) VALUES (?, ?)", (user, url))))
    db_queue.join()  # Ожидание завершения задачи
    bot.send_message(message.chat.id, "Хотелка добавлена!")

# Обработчик нажатия на кнопку "Удалить хотелку"
@bot.message_handler(func=lambda message: message.text == "Удалить хотелку")
def delete_wishlist_item(message):
    if message.from_user.id not in authorized_users:
        bot.send_message(message.chat.id, "У вас нет доступа к удалению хотелок.")
        return

    bot.send_message(message.chat.id, "Введите ссылку на хотелку, которую хотите удалить:")
    bot.register_next_step_handler(message, process_delete_wishlist_item)

def process_delete_wishlist_item(message):
    url = message.text
    user = message.from_user.first_name
    db_queue.put((execute_query, ("DELETE FROM wishlist WHERE url = ? AND user = ?", (url, user))))
    db_queue.join()  # Ожидание завершения задачи
    bot.send_message(message.chat.id, "Хотелка удалена!")


init()
# Запускаем бота
bot.polling(none_stop=True)
