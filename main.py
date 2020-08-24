import base64
import requests
import random
import telebot
from telebot import types

TOKEN = '1248279229:AAFIcyEfBr5n40l7OXoGD8d4MiAxbHDyfhw'
API = 'https://opentdb.com/api.php?amount=10&encode=base64'
AMOUNT = 1
CATEGORIES = {
      '/GeneralKnowledge': 9,
      '/EntertainmentBooks': 10,
      '/EntertainmentFilm': 11,
      '/EntertainmentVideoGames': 15,
      '/ScienceComputers': 18,
      '/ScienceMathematics': 19,
      '/Sports': 21,
      '/Geography': 22,
      '/History': 23,
      '/Art': 25,
      '/Animals': 27,
      }
CATEGORIES_STR = '\n'.join(CATEGORIES)
CURRENT_CATEGORY = ''
COUNTER = 0
COUNTER_CORRECT_ANSWERS = 0

bot = telebot.TeleBot(TOKEN)


def helper_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('/start', '/help', '/quiz')
    return markup


def get_questions(category='', amount=5):
    resp = requests.get(
        f'https://opentdb.com/api.php?amount=2&category={category}&encode=base64'
    )
    question = resp.json()['results'][0]
    incorrect_answer = []
    for answer in question["incorrect_answers"]:
        incorrect_answer.append(base64.b64decode(answer).decode())
    question_bloc = {
        'question': base64.b64decode(question["question"]).decode(),
        'correct_answer': base64.b64decode(
            question["correct_answer"]).decode(),
        'incorrect_answers': incorrect_answer,
        'category': base64.b64decode(question["category"]).decode()
    }

    return question_bloc


@bot.message_handler(commands=['start', 'help'])
def start(message):
    bot.reply_to(message, f"Hi \U0001F44B, you can start play with "
                          f"random: /quiz category \nor you can choose "
                          f"it /category", reply_markup=helper_menu())


@bot.message_handler(commands=['category'])
def category(message):
    bot.send_message(message.chat.id, f"Choose the category: \n{CATEGORIES_STR}")
    bot.register_next_step_handler(message, amount_questions)


@bot.message_handler(content_types=['text'])
def amount_questions(message):
    if message.text == '/next':
        return definition(message)
    global CURRENT_CATEGORY
    CURRENT_CATEGORY = message.text
    bot.send_message(message.chat.id, f'Write number of questions:')
    bot.register_next_step_handler(message, definition)


@bot.message_handler(commands=['next', 'quiz'])
def definition(message):
    global AMOUNT
    global CURRENT_CATEGORY
    if message.text != '/next':
        AMOUNT = int(message.text)
        CURRENT_CATEGORY = CATEGORIES.get(CURRENT_CATEGORY, '')
    question_box = get_questions(CURRENT_CATEGORY, AMOUNT)
    markup = types.InlineKeyboardMarkup()
    buttons_list = [types.InlineKeyboardButton(text=question_box['correct_answer'], callback_data='correct')]
    for answer in question_box['incorrect_answers']:
        buttons_list.append(types.InlineKeyboardButton(text=answer, callback_data='incorrect'))
    while len(buttons_list):
        markup.add(buttons_list.pop(random.randrange(len(buttons_list))))

    bot.send_message(message.chat.id, f'Question from category {question_box["category"]}: \n{question_box["question"]}', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def text_catch(call):
    global COUNTER
    global COUNTER_CORRECT_ANSWERS
    COUNTER += 1
    message_text = f'{call.data.title()}\U0000274C. Try /next question('
    if call.data == 'correct':
        COUNTER_CORRECT_ANSWERS += 1
        message_text = f'{call.data.title()}\u2705. Try /next question)'
    if COUNTER == AMOUNT:
        message_text = f'{call.data.title()}. Looks great\U0001F389 !!!' \
                       f'\nYour number of correct answers: {COUNTER_CORRECT_ANSWERS}' \
                       f'\nTry another category /category)' \

        COUNTER = 0
        COUNTER_CORRECT_ANSWERS = 0

    bot.reply_to(call.message, message_text)


bot.polling()
