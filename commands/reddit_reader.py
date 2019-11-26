"""
This module pulls memes from reddit using feedparser and BeautifulSoup
as a CommandHandler for a Telegrambot
"""

# import datetime
import time
import feedparser


from bs4 import BeautifulSoup as bs

from telegram import ParseMode
from telegram.ext import CommandHandler

from constants import REDDIT

def get_reddit_meme(update, context):
    """ get acces reddit using feedparser and parse html using BeautifulSoup """
    bot = context.bot
    chat_id = update.message.chat_id

    feed = feedparser.parse(REDDIT)

    # update_tag = feed['feed']['updated']

    subtitle = feed['feed']['subtitle']
    posts = feed['entries']

    # print(len(posts))

    bot.send_message(chat_id, subtitle, parse_mode=ParseMode.MARKDOWN)

    img_links = []

    for i in range(3):
        post = posts[i]

        # access html
        post_content_html = post['content'][0]['value']

        bs_content = bs(post_content_html, "xml")

        span = bs_content.find("span")
        img_links.append(span.find("a", href=True)['href'])

    for img in img_links:
        time.sleep(1)
        bot.send_photo(update.message.chat_id, img, caption="Meme!")

reddit = CommandHandler("reddit", get_reddit_meme)
