import base64
import requests
import random
import telebot
from telebot import types

token = '1248279229:AAFIcyEfBr5n40l7OXoGD8d4MiAxbHDyfhw'
api = 'https://opentdb.com/api.php?amount=10&encode=base64'
bot = telebot.TeleBot(token)
categories = {
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
categories_str = '\n'.join(categories)
current_category = ''
counter = 0
correct_answers = 0


def helper_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('/start', '/help', '/quiz')
    return markup


def get_questions(category):
    resp = requests.get(
        f'https://opentdb.com/api.php?amount=1&category={category}&encode=base64'
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
    bot.reply_to(message, f"Start test /quiz", reply_markup=helper_menu())


@bot.message_handler(commands=['quiz'])
def quiz(message):
    bot.send_message(message.chat.id, f"Chuse category: \n{categories_str}")
    bot.register_next_step_handler(message, definition)


@bot.message_handler(commands=['next'])
def definition(message):
    global current_category
    if message.text != '/next':
        question_box = get_questions(categories.get(message.text, ''))
        current_category = categories.get(message.text, '')
    question_box = get_questions(current_category)
    markup = types.InlineKeyboardMarkup()
    buttons_list = [types.InlineKeyboardButton(text=question_box['correct_answer'], callback_data='correct')]
    for answer in question_box['incorrect_answers']:
        buttons_list.append(types.InlineKeyboardButton(text=answer, callback_data='incorrect'))
    while len(buttons_list):
        markup.add(buttons_list.pop(random.randrange(len(buttons_list))))

    bot.send_message(message.chat.id, f'Question from category {question_box["category"]}: \n{question_box["question"]}', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def text_catch(call):
    global counter
    global correct_answers
    print(counter)
    counter += 1
    message_text = f'{call.data.title()}( \U0001F625 Try /next qustion'
    if call.data == 'correct':
        correct_answers += 1
        message_text = f'{call.data.title()}. Looks great!!! try /next question) \U0001F389'
    if counter == 5:
        message_text = f'{call.data.title()}. Looks great!!! \U0001F389 \nTry enouzer category /quiz) total: {correct_answers}'
        counter = 0
        correct_answers = 0

    bot.reply_to(call.message, message_text)


bot.polling()
