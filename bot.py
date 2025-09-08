import telebot
from telebot import types
import random
import threading
import time

TOKEN = "Paste token here"
bot = telebot.TeleBot(TOKEN, parse_mode=None)

game = {
    "teams": {},
    "team_order": [],
    "current_team_index": 0,
    "current_team": None,
    "current_word": None,
    "round_time": 111,
    "round_number": 0,
    "chat_id": None,
    "words_pool": [],
    "round_active": False,
    "time_left": 0,
    "timer_thread": None,
    "last_word_pending": False,
    "score_to_win": 5,
}

with open("simple_words.txt", "r", encoding="utf-8") as f:
    simple_words = [line.strip().upper() for line in f if line.strip()]

with open("hard_words.txt", "r", encoding="utf-8") as f:
    hard_words = [line.strip().upper() for line in f if line.strip()]


def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton("✅ Почати нову гру")
    btn2 = types.KeyboardButton("ℹ️ Правила")
    markup.add(btn1, btn2)
    return markup


def start_button():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ Почати гру", callback_data="start_game"))
    return markup


def word_buttons():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ Вгадано", callback_data="guessed"))
    markup.add(types.InlineKeyboardButton("❌ Пропустити", callback_data="skip"))
    return markup


def difficulty_buttons():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Прості слова", callback_data="simple"))
    markup.add(types.InlineKeyboardButton("Складні слова", callback_data="hard"))
    return markup


def next_round_button():
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("➡ Наступний раунд", callback_data="next_round")
    )
    return markup


@bot.message_handler(func=lambda message: message.text == "✅ Почати нову гру")
def handle_start_game(message):
    start_game(message)


@bot.message_handler(func=lambda message: message.text == "ℹ️ Правила")
def send_rules(message):
    rules = (
        "📜 Правила гри 📜\n\n"
        "1. Гра розрахована на 2 команди.\n"
        "2. Кожна команда по черзі отримує слова для відгадування.\n"
        "3. Спільнокореневі слова використовувати заборонено.\n"
        "4. За кожне вгадане слово команда отримує 1 бал.\n"
        "5. За кожне пропущене слово команда втрачає 1 бал.\n"
        "6. Раунд триває 111 секунд.\n"
        "7. Перемагає команда, яка першою набере 5 балів.\n\n"
        "🍀 Удачі! 🍀"
    )
    bot.send_message(message.chat.id, rules)


# Старт гри
@bot.message_handler(commands=["start"])
def start(message):
    chat_id = message.chat.id
    game["chat_id"] = chat_id
    bot.send_message(
        chat_id,
        "🎮 Головне меню 🎮",
        reply_markup=main_menu(),
    )


# Ініціалізація гри
@bot.callback_query_handler(func=lambda call: call.data == "start_game")
def start_game(call):
    chat_id = game["chat_id"]
    game["teams"] = {}
    game["team_order"] = []
    game["current_team_index"] = 0
    game["round_number"] = 0
    bot.send_message(chat_id, "Гра починається! Введіть назву першої команди:")
    bot.register_next_step_handler_by_chat_id(chat_id, get_team_name, team_number=1)


def get_team_name(message, team_number):
    name = message.text.strip()
    game["teams"][name] = {"score": 0}
    game["team_order"].append(name)
    chat_id = game["chat_id"]
    if team_number == 1:
        bot.send_message(chat_id, "Введіть назву другої команди:")
        bot.register_next_step_handler_by_chat_id(chat_id, get_team_name, team_number=2)
    else:
        bot.send_message(
            chat_id,
            "Обидві команди зареєстровані. Виберіть складність слів:",
            reply_markup=difficulty_buttons(),
        )


# Вибір складності
@bot.callback_query_handler(func=lambda call: call.data in ["simple", "hard"])
def choose_difficulty(call):
    if call.data == "simple":
        game["words_pool"] = simple_words.copy()
    else:
        game["words_pool"] = hard_words.copy()
    chat_id = game["chat_id"]
    bot.send_message(chat_id, f"Ви обрали: {call.data}. Починаємо гру!")
    start_team_round()


# Початок раунду для команди
def start_team_round():
    if game["round_number"] == 0:
        game["round_number"] = 1
    game["current_team"] = game["team_order"][game["current_team_index"]]
    game["round_active"] = True
    game["time_left"] = game["round_time"]
    game["last_word_pending"] = False
    send_new_word()

    # старт таймера
    game["timer_thread"] = threading.Thread(target=round_timer)
    game["timer_thread"].start()


def round_timer():
    while game["time_left"] > 0 and game["round_active"]:
        time.sleep(1)
        game["time_left"] -= 1

    if game["round_active"]:
        game["round_active"] = False
        game["last_word_pending"] = True
        bot.send_message(
            game["chat_id"], "⏰ Час вийшов! Можна надіслати останню відповідь."
        )
        bot.send_message(
            game["chat_id"],
            "Натисніть кнопку, щоб почати наступний раунд.",
            reply_markup=next_round_button(),
        )


def send_new_word():
    if not game["words_pool"]:
        bot.send_message(game["chat_id"], "Слова закінчилися! Раунд завершено.")
        game["round_active"] = False
        bot.send_message(
            game["chat_id"],
            "Натисніть кнопку, щоб почати наступний раунд.",
            reply_markup=next_round_button(),
        )
        return
    word = random.choice(game["words_pool"])
    game["current_word"] = word.upper()
    game["words_pool"].remove(word)
    chat_id = game["chat_id"]
    bot.send_message(
        chat_id,
        f"➡️ Раунд <b>{game['round_number']}</b>\n"
        f"👥 Команда: <b>{game['current_team']}</b>\n\n"
        f"⏱️ {game['time_left']} секунд ⏱️\n\n"
        f"🔤 <b>{game['current_word']}</b> 🔤",
        parse_mode="HTML",
        reply_markup=word_buttons(),
    )


# Обробка натискань Вгадано/Пропустити
@bot.callback_query_handler(func=lambda call: call.data in ["guessed", "skip"])
def handle_guess(call):
    if not game["round_active"] and not game["last_word_pending"]:
        bot.answer_callback_query(call.id, "Раунд ще не запущений або час вийшов.")
        return

    team = game["teams"][game["current_team"]]
    if call.data == "guessed":
        team["score"] += 1
    elif call.data == "skip":
        team["score"] -= 1

    bot.send_message(
        call.message.chat.id, f"Рахунок {game['current_team']}: {team['score']}"
    )

    if team["score"] >= game["score_to_win"]:
        bot.send_message(
            call.message.chat.id, f"🏆 Команда '{game['current_team']}' перемогла!"
        )
        game["round_active"] = False
        # Кнопка для початку нової гри
        bot.send_message(
            call.message.chat.id,
            "Натисніть кнопку, щоб почати нову гру.",
            reply_markup=start_button(),
        )
        return

    if game["round_active"]:
        send_new_word()
    else:
        # обробка останнього слова після часу
        game["last_word_pending"] = False


# Початок наступного раунду
@bot.callback_query_handler(func=lambda call: call.data == "next_round")
def next_round(call):
    game["current_team_index"] = (game["current_team_index"] + 1) % len(
        game["team_order"]
    )
    if game["current_team_index"] == 0:
        game["round_number"] += 1
    start_team_round()


# Запуск бота
bot.infinity_polling()
