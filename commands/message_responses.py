"""
This module generates responses to the input of the user.
"""
import random

from commands.message_filters import hello_filter, question_filter, leuk_filter, yourmom_filter

import emoji

from telegram import ParseMode
from telegram.ext import MessageHandler

from constants import REASONS

def hello(update, context):
    """ greets the user back """
    chat_id = update.message.chat_id
    user = update.message.from_user
    bot = context.bot

    msg = f"Hallo {user.first_name}!"
    bot.send_message(chat_id=chat_id, text=msg)

def question(update, context):
    """ replies to questions from the user """
    bot = context.bot
    user = update.message.from_user
    inc_msg = update.message.text

    # answer why questions with a reasons from database
    if 'waarom' in str.lower(update.message.text):

        # return a random reason from file
        with open(REASONS) as file:
            lines = file.readlines()
            msg = random.choice(lines)

    # answer other questions with
    else:
        options = [
            f"Vraag het maar niet aan mij, ik ben niet alwetend.",
            ("https://lmgtfy.com/?q=" + inc_msg.replace(" ", "+") + "&pp=1&s=g&t=w"),
            f"Ja he dat weet ik toch ook niet, google dat maar ff {user.first_name}..."
            ]

        msg = random.choice(options)
    bot.send_message(chat_id=update.message.chat_id, text=msg,
                     parse_mode=ParseMode.MARKDOWN)

def leuk(update, context):
    """ compliments the user """
    chat_id = update.message.chat_id
    user = update.message.from_user
    bot = context.bot

    options = [
        f"Je bent zelf leuk {user.first_name}!",
        "Jij leukerd!"]

    msg = random.choice(options)
    bot.send_message(chat_id=chat_id, text=msg)

def yourmom(update, context):
    """ tries to make yo mama jokes """
    chat_id = update.message.chat_id
    bot = context.bot

    options = [
        "Dat zei je mama gisteren ook.",
        emoji.emojize("Dat zei je moeder gisteren ook. :woman_raising_hand:"),
        "Ik zou nu een je moeder grap kunnen maken maar ik houd me in.",
        emoji.emojize("Je mama is lief hoor. :woman_raising_hand:")]

    msg = random.choice(options)

    bot.send_message(chat_id=chat_id, text=msg)

hello = MessageHandler(hello_filter, hello)
question = MessageHandler(question_filter, question)
leuk = MessageHandler(leuk_filter, leuk)
yourmom = MessageHandler(yourmom_filter, yourmom)
