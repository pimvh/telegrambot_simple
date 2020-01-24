#!/usr/bin/env python3
"""
The module below implements a telegram bot with a number of commandhandlers (in Dutch):
- some general commands, like /start and /help.
- /beer for a beer database
- some message filter than generate responses to the user.
- a reddit reader that pulls memes from me_irl
- a news reader (in development)
"""

__author__ = """Pim van Helvoirt"""
__copyright__ = "None"
__credits__ = [""]
__license__ = "GPL"
__version__ = "1.0.3"
__maintainer__ = "Pim van helvoirt"
__email__ = "pim.van.helvoirt@home.nl"
__status__ = "Production"

import logging

from commands.general import start, help_msg, code

from commands.beer_base import beer_conv
from commands.message_responses import (hello, leuk, question,
                                        yourmom, hardtimes)
from commands.news_reader import news, view_feeds
from commands.reddit_reader import reddit_conv
from commands.weather_report import weer

from telegram.ext import Updater

from constants import TELEGRAM_TOKEN

def main():
    """ Create the updater and pass it your a token
        and add handlers to the bot. """

    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)

    dp = updater.dispatcher

    # log errors on a basic level
    logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                        level=logging.INFO)

    dp.add_handler(start)
    dp.add_handler(help_msg)
    dp.add_handler(code)

    dp.add_handler(beer_conv)
    dp.add_handler(hardtimes)
    dp.add_handler(hello)
    dp.add_handler(leuk)
    dp.add_handler(news)
    dp.add_handler(question)
    dp.add_handler(reddit_conv)
    dp.add_handler(view_feeds)
    dp.add_handler(weer)
    dp.add_handler(yourmom)

    # updater.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
