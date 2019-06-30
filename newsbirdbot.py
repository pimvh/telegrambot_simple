#!/usr/bin/env python

"""
"""

__author__ = """Pim van Helvoirt"""
__copyright__ = "None"
__credits__ = [""]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "None"
__email__ = "pim.van.helvoirt@home.nl"
__status__ = "Production"

from telegram.ext import Updater, CommandHandler
import feedparser
import time


# "NRC": "https://www.nrc.nl/rss/",
FEEDS = {
"Volkskrant": "https://www.volkskrant.nl/voorpagina/rss.xml",
"Trouw": "https://www.trouw.nl/voorpagina/rss.xml"}

UPDATE_FREQ = 300

TEST = "http://feedparser.org/docs/examples/rss20.xml"

def hello(bot, update):
    telegram_user = update.message.from_user
    update.message.reply_text(f"Hello {telegram_user.first_name}")

def weather(bot, update):
    # TODO: weer api afmaken
    telegram_user = update.message.from_user
    update.message.reply_text('Hello the weather today is: ')

def get_news(bot, update):
    """ https://pythonhosted.org/feedparser/introduction.html"""

    times_parsed = [[]]*len(FEEDS)
    print(times_parsed)

    publish_times = set()

    # get the oldest pubdate of each RSS feed
    for i, feed in enumerate(FEEDS):

        try:
            fd = feedparser.parse(FEEDS[feed])

            for entry in fd.entries:
                publish_times.add(entry.published_parsed)

            times_parsed[i] = min(publish_times)

            print(f"RSS feed {feed} is {len(fd.entries)} long.")
            # print(times_parsed)

        except Exception as e:
            print(e)

    # keep reading feeds
    while True:

        for i, feed in enumerate(FEEDS):

            # get the feed and update the pub time
            pud_dates[i] = get_feed(bot, update, FEEDS[feed],
                                    times_parsed[i])

            print(f"sleeping {UPDATE_FREQ}")
            time.sleep(UPDATE_FREQ)

def get_feed(bot, update, feedlink, pub_time):
    """ returns the new article of a given rss feed with a etag and modified tag """
    try:

        feed = feedparser.parse(feedlink)
        # loop over the feed
        for entry in feed.entries:

            # skip if entry is before last pubdate
            if entry.published_parsed < pub_time:
                continue

            out = format_rss(entry)

            # TEMP: output to terminal
            print(out)
            update.message.reply_text(f"{out}", parse_mode='markdown',
                                      disable_web_page_preview=True)
            time.sleep(1)

            # grab the last published time
            pubdate = entry.published_parsed

        return pubdate

    except Exception as e:
        print(e)

def format_rss(text):
    """ does some nice markup for the RSS feed """
    s = ""
    s += ('*' + text.title + '*' + '\n\n' + text.summary + '\n\n' +
         text.link)
    return s

def view_feeds(bot, update):
    mes = "This bot pulls from the following feeds: "
    update.message.reply_text(mes + f"\n {FEEDS.keys()}")

def main():
    """ Create the Updater and pass it your bot's token. """

    # token is in other file for security
    with open('token.txt') as file:
        token = file.readline().strip()
        print(token)

    updater = Updater(token)

    updater.dispatcher.add_handler(CommandHandler('hello', hello))
    updater.dispatcher.add_handler(CommandHandler('weather', weather))
    updater.dispatcher.add_handler(CommandHandler('feeds', view_feeds))
    updater.dispatcher.add_handler(CommandHandler('news', get_news))
    # updater.add_error_handler(error)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
