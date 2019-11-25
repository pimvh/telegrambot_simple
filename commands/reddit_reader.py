import feedparser

from telegram import ParseMode
from telegram.ext import CommandHandler

from constants import REDDIT

def reddit(update, context):
    bot = context.bot
    feed = feedparser.parse(REDDIT)

    print(feed)

    # for i in range(3):
    #     bot.send_message(text=feed[i],
    #                      parse_mode=ParseMode.MARKDOWN)

reddit = CommandHandler("reddit", reddit)
