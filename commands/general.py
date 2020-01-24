"""
This module implements general commands for the Telegram bot, namely start and help
"""

from telegram import ParseMode
from telegram.ext import CommandHandler

def start_func(update, context):
    """ greets the user on starting the bot """
    bot = context.bot
    msg = "Hallo! Leuk dat je er bent!"

    bot.send_message(chat_id=update.message.chat_id, text=msg,
                     reply_to_message_id=update.message.message_id,
                     parse_mode=ParseMode.MARKDOWN)
    help_func(update, context)

def help_func(update, context):
    """ displays a help message (Dutch) """

    bot = context.bot
    msg = """ Deze bot heeft de volgende *commandos*:
    - /help : laat dit bericht zien
    - /weer _[locatie]_ : geeft weer terug op locatie
    - /hallo : krijg een groet van deze bot
    - /waarom : krijg een willekeurige reden terug
    - /bier: een database om bij te houden: van wie je bier krijgt of aan wie je bier schuldig bent.
    - /meme: haal memes van de reddit pagina me_irl of ik_ihe.
    - /code: bekijk de code van deze robot.
    """

    bot.send_message(chat_id=update.message.chat_id, text=msg,
                     reply_to_message_id=update.message.message_id,
                     parse_mode=ParseMode.MARKDOWN)

def view_code_func(update, context):
    """ shows user where to find bot code (Dutch) """
    bot = context.bot
    msg = """ De code van deze bot is geschreven met de Python-telegram-bot wrapper en staat online op [Github](https://github.com/pimvh/telegrambot_simple).
    """

    bot.send_message(chat_id=update.message.chat_id, text=msg,
                     reply_to_message_id=update.message.message_id,
                     parse_mode=ParseMode.MARKDOWN)

start = CommandHandler("start", start_func)
help_msg = CommandHandler("help", help_func)
code = CommandHandler("code", view_code_func)
