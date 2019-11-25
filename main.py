#!/usr/bin/env python3
"""
The module below implements a telegram bot with a number of commandhandlers:
- # TODO:
"""

__author__ = """Pim van Helvoirt"""
__copyright__ = "None"
__credits__ = [""]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Pim van helvoirt"
__email__ = "pim.van.helvoirt@home.nl"
__status__ = "Production"

import collections
import datetime
import os
import logging

import requests
import sys
import time

# telegram python wrapper
from telegram.ext import (
    CommandHandler,
    Updater,
)

# from telegram.ext import (CommandHandler, BaseFilter, Filters, MessageHandler)
from telegram.ext import CommandHandler

from constants import TELEGRAM_TOKEN

from commands.beer_base import beer_conv
from commands.message_responses import hello, leuk, question, yourmom
from commands.news_reader import news, view_feeds
from commands.reddit_reader import reddit
from commands.weather_report import weer

# Token filename

def start(update, context):
    bot = context.bot
    msg = "Hallo! Leuk dat je er bent!"

    bot.send_message(chat_id=update.message.chat_id, text=msg,
                        parse_mode=telegram.ParseMode.MARKDOWN)
    help(update, context)

def help(update, context):
    """ displays a help message (Dutch) """

    bot = context.bot
    msg = """ Deze bot heeft de volgende *commandos*:
    - /help : laat dit bericht zien
    - /weer _[locatie]_ : geeft weer terug op locatie
    - /hallo : krijg een groet van deze bot
    - /waarom : krijg een willekeurige reden terug
    - /bier: een database om bij te houden: van wie je bier krijgt of aan wie je bier schuldig bent
    """

    bot.send_message(chat_id=update.message.chat_id, text=msg,
                        parse_mode=telegram.ParseMode.MARKDOWN)

def main():
    """ Create the updater and pass it your bot"s token
        and add the handlers to the bot. """

    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)

    dp = updater.dispatcher

    # log errors
    logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                        level=logging.INFO)

    dp.add_handler(CommandHandler("help", help))

    dp.add_handler(beer_conv)
    dp.add_handler(hello)
    dp.add_handler(leuk)
    dp.add_handler(news)
    dp.add_handler(question)
    dp.add_handler(reddit)
    dp.add_handler(view_feeds)
    dp.add_handler(weer)
    dp.add_handler(yourmom)

    # updater.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
