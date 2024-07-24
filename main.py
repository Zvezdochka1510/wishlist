import telebot
from telebot import types
import sqlite3

# Создаем экземпляр бота
bot = telebot.TeleBot("7405564479:AAFF1Z8iNYSxqmtedDcjMYay8Xp74C8GFeg")


# Создаем подключение к базе данных
conn = sqlite3.connect('wishlist.db')

# Создаем таблицу wishlist, если она еще не существует
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS wishlist (
        id INTEGER PRIMARY KEY,
        user TEXT,
        url TEXT
    )
""")
conn.commit()

# Добавляем столбец url в таблицу wishlist, если его еще нет
try:
    cursor.execute("""
        ALTER TABLE wishlist ADD COLUMN IF NOT EXISTS url TEXT
    """)
except sqlite3.OperationalError:
    # Обработка ошибки, если таблица wishlist не существует
    pass

# Список пользователей, которые могут использовать бота
authorized_users = [2045383874, 998211350]

# База данных хотелок
wishlist = {
    'Настя': [],
    'Даня': []
}


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
    cursor.execute("SELECT url FROM wishlist WHERE user = 'Настя'")
    wishlist_items = cursor.fetchall()
    if wishlist_items:
        wishlist_str = '\n'.join([item[0] for item in wishlist_items])
        bot.send_message(message.chat.id, f"Вот хотелки Насти:\n{wishlist_str}")
    else:
        bot.send_message(message.chat.id, "У Насти пока нет хотелок.")


# Обработчик нажатия на кнопку "Данины хотелки"
@bot.message_handler(func=lambda message: message.text == "Данины хотелки")
def show_danya_wishlist(message):
    cursor.execute("SELECT url FROM wishlist WHERE user = 'Даня'")
    wishlist_items = cursor.fetchall()
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
        user = message.from_user.first_name
        cursor.execute("INSERT INTO wishlist (user, url) VALUES (?, ?)", (user, message.text))
        conn.commit()

    # Добавляем ссылку в список хотелок
    #if message.from_user.first_name == '🦋Nestia🦋':
    #    wishlist['Настя'].append(message.text)
    #elif message.from_user.first_name == 'Даниил':
   #     wishlist['Даня'].append(message.text)
    #else:
    #    bot.send_message(message.chat.id, "У вас нет доступа к добавлению хотелок.")
    #    return

    # Сообщаем об успешном добавлении
    bot.send_message(message.chat.id, "Хотелка успешно добавлена!")

# Обработчик нажатия на кнопку "Удалить хотелку"
@bot.message_handler(func=lambda message: message.text == "Удалить хотелку")
def remove_wishlist_item(message):
    # Запрашиваем ссылку на хотелку для удаления
    bot.send_message(message.chat.id, "Отправьте ссылку на хотелку для удаления:")
    bot.register_next_step_handler(message, process_remove_wishlist_item)


def process_remove_wishlist_item(message):
    # Проверяем, что ссылка валидная
    if not message.text.startswith('http'):
        bot.send_message(message.chat.id, "Неправильный формат ссылки. Попробуйте снова.")
        bot.register_next_step_handler(message, process_remove_wishlist_item)
        return

    # Удаляем ссылку из базы данных
    user = message.from_user.first_name
    cursor.execute("DELETE FROM wishlist WHERE user = ? AND url = ?", (user, message.text))
    conn.commit()


# Обработчик нажатия на кнопку "Удалить хотелку"
#@bot.message_handler(func=lambda message: message.text == "Удалить хотелку")
#def remove_wishlist_item(message):
    # Запрашиваем ссылку на хотелку для удаления
 #   bot.send_message(message.chat.id, "Отправьте ссылку на хотелку для удаления:")
  #  bot.register_next_step_handler(message, process_remove_wishlist_item)


#def process_remove_wishlist_item(message):
    # Удаляем ссылку из списка хотелок
    #if message.text in wishlist['Настя']:
    #    wishlist['Настя'].remove(message.text)
    #elif message.text in wishlist['Даня']:
    #    wishlist['Даня'].remove(message.text)
   # else:
    #    bot.send_message(message.chat.id, "Такой ссылки нет в списке хотелок.")
    #    return

    # Сообщаем об успешном удалении
    bot.send_message(message.chat.id, "Хотелка успешно удалена!")


# Закрываем соединение с базой данных
cursor.close()
conn.close()

# Запуск бота
bot.polling()
