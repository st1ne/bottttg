import telebot
import sqlite3
from telebot import types
from threading import Lock

# Создание базы данных и таблицы
try:
    with sqlite3.connect('D:/telegram_bot/quiz_responses.db', check_same_thread=False) as conn:
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS quiz (user_id INTEGER, question TEXT, answer TEXT)')
        conn.commit()

        # Ваш код для работы с базой данных

except sqlite3.Error as e:
    print("Ошибка при работе с базой данных:", str(e))





# Инициализация бота
bot = telebot.TeleBot('6247842113:AAGUe7X0DZ9LhojO8lEFwsQwmRNM12FziR0')

# Список вопросов и правильных ответов
questions = [
    {
        "question": "Хотите ли вы пройти опрос?",
        "options": ["Да", "Нет"],
        "correct_answer": "Да",
        "points": 0
    },
    {
        "question": "Какая столица Франции?",
        "options": ["Париж", "Москва", "Лондон"],
        "correct_answer": "Париж",
        "points": 10
    },
    {
        "question": "Сколько планет в солнечной системе?",
        "options": ["6", "8", "10"],
        "correct_answer": "8",
        "points": 15
    },
    {
        "question": "Кто написал произведение 'Война и мир'?",
        "options": ["Фёдор Достоевский", "Лев Толстой", "Антон Чехов"],
        "correct_answer": "Лев Толстой",
        "points": 20
    },
    # Добавьте остальные вопросы с правильными ответами и количеством баллов
    {
        "question": "Какой город является столицей Японии?",
        "options": ["Токио", "Киото", "Осака"],
        "correct_answer": "Токио",
        "points": 12
    },
    {
        "question": "Какой химический элемент имеет символ 'Fe'?",
        "options": ["Фосфор", "Железо", "Фтор"],
        "correct_answer": "Железо",
        "points": 8
    },
    {
        "question": "Как называется главный герой романа 'Мастер и Маргарита'?",
        "options": ["Иван Иванович", "Михаил Иванович", "Воланд"],
        "correct_answer": "Воланд",
        "points": 15
    },
    {
        "question": "Кто изображен на логотипе компании Apple?",
        "options": ["Исаак Ньютон", "Альберт Эйнштейн", "Стив Джобс"],
        "correct_answer": "Исаак Ньютон",
        "points": 10
    },
    {
        "question": "Какое животное является символом Годика в китайском календаре?",
        "options": ["Змея", "Лошадь", "Обезьяна"],
        "correct_answer": "Обезьяна",
        "points": 7
    },
    {
        "question": "Какой самый крупный океан на Земле?",
        "options": ["Тихий", "Атлантический", "Индийский"],
        "correct_answer": "Тихий",
        "points": 13
    },
    {
        "question": "Какой цвет получится при смешении синего и желтого?",
        "options": ["Фиолетовый", "Зеленый", "Оранжевый"],
        "correct_answer": "Зеленый",
        "points": 8
    }
]

# Словарь для хранения ответов пользователей
user_answers = {}
user_answers_lock = Lock()  # Блокировка для синхронизации доступа к словарю user_answers

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    with user_answers_lock:
        user_answers[chat_id] = {}  # Создаем пустой словарь для пользователя
    send_question(chat_id, 0)

# Функция для отправки вопросов пользователю
def send_question(chat_id, question_index):
    if question_index < len(questions):
        question = questions[question_index]["question"]
        options = questions[question_index]["options"]
        send_options_question(chat_id, question, options)
    else:
        calculate_score(chat_id)

# Функция для отправки вопроса с вариантами ответов
def send_options_question(chat_id, question, options):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [types.KeyboardButton(option) for option in options]
    markup.add(*buttons)
    bot.send_message(chat_id, question, reply_markup=markup)

# Обработчик текстовых сообщений
@bot.message_handler(func=lambda message: True)
# Обработчик текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    with user_answers_lock:
        # Проверяем, есть ли уже ответы пользователя в словаре
        if chat_id not in user_answers:
            user_answers[chat_id] = {}  # Если ответов нет, создаем пустой словарь для пользователя

        question_index = len(user_answers[chat_id])

        # Обработка ответа пользователя на первый вопрос (о пройти опрос или нет)
        if question_index == 0:
            answer = message.text
            if answer.lower() == "нет":
                bot.send_message(chat_id, "Вы отказались от прохождения опроса.")
                return

        # Если все вопросы уже заданы, игнорируем дополнительные ответы пользователя
        if question_index >= len(questions):
            return

        # Сохранение ответа пользователя в словаре
        user_answers[chat_id][question_index] = message.text

        # Сохранение ответа пользователя в базе данных
        cursor.execute('INSERT INTO quiz VALUES (?, ?, ?)', (user_id, questions[question_index]["question"], message.text))
        conn.commit()

    if question_index + 1 < len(questions):
        send_question(chat_id, question_index + 1)
    else:
        calculate_score(chat_id)

# Функция для расчета баллов и вывода итогового сообщения
def calculate_score(chat_id):
    with user_answers_lock:
        user_id = list(user_answers[chat_id].keys())[0]
    total_score = 0
    for question_index, answer in user_answers[chat_id].items():
        correct_answer = questions[question_index]["correct_answer"]
        points = questions[question_index]["points"]
        if answer == correct_answer:
            total_score += points

    max_score = 100  # Максимальное количество баллов
    score_percentage = (total_score / max_score) * 100

    bot.send_message(chat_id, f"Спасибо за ответы! Ваш общий балл: {total_score}/{max_score} ({score_percentage:.2f}%)")

# Запуск бота
bot.polling()
