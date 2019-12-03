"""
This module pulls memes from reddit using feedparser and BeautifulSoup
as a CommandHandler for a Telegrambot
"""

import random
import time
import emoji
import feedparser


from bs4 import BeautifulSoup as bs

from telegram import ParseMode, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (MessageHandler, CommandHandler,
                          ConversationHandler)

from constants import REDDIT
from commands.message_filters import redditpage_filter

CHOICE = range(1)

def meme(update, context):
    bot = context.bot
    chat_id = update.message.chat_id
    msg = "Selecteer maar een pagina voor je verse memes."
    reply_keyboard = [[key for key in REDDIT.keys()]]

    bot.send_message(chat_id=chat_id, text=msg,
                      parse_mode=ParseMode.MARKDOWN,
                      reply_to_message_id=update.message.message_id,
                      reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                       one_time_keyboard=True,
                                                       selective=True))
    return CHOICE

def get_memes(update, context):
    """ get acces redditReplyKeyboardMarkup using feedparser and parse html using BeautifulSoup """
    bot = context.bot
    chat_id = update.message.chat_id
    inc_msg = update.message.text

    page = REDDIT[inc_msg]
    feed = feedparser.parse(page)

    # print(feed, '\n\n')
    # update_tag = feed['feed']['updated']

    msg = f"'*' {feed['feed']['title']} '*'"

    if feed['feed'].get('subtitle', 0):
        subtitle = feed['feed']['subtitle']
        msg = f"\n{subtitle}"
        bot.send_message(chat_id, msg,
                         reply_to_message_id=update.message.message_id,
                         parse_mode=ParseMode.MARKDOWN)

    posts = feed['entries']

    img_links = []

    for i in range(4):
        if i > len(posts) - 1:
            break

        post = posts[i]

        # access html
        post_content_html = post['content'][0]['value']

        bs_content = bs(post_content_html, "xml")
        # print( '\n\n', post_content_html, '\n\n')
        span = bs_content.find("span")
        # print(span, '\n\n')
        if span:
            img_links.append(span.find("a", href=True)['href'])

    captions = [emoji.emojize(':grinning_face:') * 2,
                emoji.emojize(':face_with_tears_of_joy:') * 3,
                emoji.emojize(':rolling_on_the_floor_laughing:') * 2,
                "*ademt hard door neus*",
                emoji.emojize(':upside-down_face:'),
                emoji.emojize(':thinking_face:') * 3]

    for img in img_links:
        time.sleep(1)
        bot.send_photo(update.message.chat_id, img,
                       caption=random.choice(captions), parse_mode=ParseMode.MARKDOWN,
                       reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END

def meme_fallback(update, context):
    bot = context.bot
    msg = "Joe!"

    bot.send_message(chat_id=update.message.chat_id, text=msg,
                     parse_mode=ParseMode.MARKDOWN,
                     reply_to_message_id=update.message.message_id,
                     reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END

reddit_conv = ConversationHandler(
    entry_points=[CommandHandler("meme", meme)],
    states={CHOICE: [MessageHandler(redditpage_filter, get_memes)],},
    fallbacks=[CommandHandler("exit", meme_fallback)],
    name="Memeversatie",)
