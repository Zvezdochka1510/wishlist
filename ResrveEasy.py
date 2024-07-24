import datetime

import psycopg2
import telebot
from apscheduler.schedulers.background import BlockingScheduler

# Настройка соединения с базой данных Postgres
conn = psycopg2.connect(
    host="localhost",
    database="postgres",
    user="postgres",
    password="postgres"
)

# Настройка Telegram бота
bot = telebot.TeleBot("7405564479:AAFF1Z8iNYSxqmtedDcjMYay8Xp74C8GFeg")


# Настройка планировщика задач
# scheduler = apscheduler.scheduler.Scheduler()

# Получение списка зарезервированных столов на текущий день
def get_reserved_users():
    today = datetime.date.today()
    cursor = conn.cursor()
    query = """
    SELECT *
    FROM booking
    WHERE CAST(time AS DATE) = %s
    """
    cursor.execute(query, (today,))
    results = cursor.fetchall()
    return results


# Отправка напоминаний пользователям
def send_reminders():
    users = get_reserved_users()
    for user in users:
        # user_id, telegram_link = user
        message = f'Напоминаем о вашем бронировании сегодня в ресторане:\n {user}'
        user_id = 2045383874
        bot.send_message(user_id, message)


# Запуск бота
def main():
    scheduler = BlockingScheduler()
    scheduler.add_job(send_reminders, 'interval', seconds=3)

    # Запуск планировщика задач
    scheduler.start()
    # Запуск бота
    bot.polling()


if __name__ == "__main__":
    main()
