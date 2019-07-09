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

import feedparser
from functools import wraps
import datetime
import random
import requests
import sys
import time

import logging

from geopy.geocoders import Nominatim
from telegram.ext import Updater, CommandHandler, BaseFilter
import telegram.ext

DARKYSKY = "https://api.darksky.net/forecast"

# "Trouw": "https://www.trouw.nl/voorpagina/rss.xml"
FEEDS = {
# "Volkskrant": "https://www.volkskrant.nl/voorpagina/rss.xml",
"NRC": "https://www.nrc.nl/rss/",
}

# TODO: schrijf start functie
def start(bot, update):
    pass

def help(bot, update):
    msg = """ Deze bot heeft de volgende *commandos*:
    - /help : laat dit bericht zien
    - /weer _[locatie]_ : geeft weer terug op locatie (standaard locatie Amsterdam)
    - /hallo : krijg een groet van deze bot
    - /waarom : krijg een willekeurige reden terug
    """
    bot.send_message(chat_id=update.message.chat_id, text=msg,
                     parse_mode=telegram.ParseMode.MARKDOWN)

def hello(bot, update):
    telegram_user = update.message.from_user
    update.message.reply_text(f"Hallo {telegram_user.first_name}!")

    # bot.send_message(chat_id=update.message.chat_id,
    #              text="*bold* _italic_ `fixed width font` [link](http://google.com).",
    #              parse_mode=telegram.ParseMode.MARKDOWN)

def weather(bot, update):
    chat_id = update.message.chat_id
    #board = ['Amsterdam','Anders']
    # kb = [[telegram.KeyboardButton('Amsterdam')]]
    # kb, one_time_keyboard=True

    # reply_markup=kb_markup

    try:
        location_str = str.split(update.message.text, " ")[1]
    except:
        bot.send_message(chat_id=chat_id, text="Geen locatie gegeven. Standaard: Amsterdam")
        location_str = "Amsterdam"

    geolocator = Nominatim()
    location = geolocator.geocode(location_str)

    if location is None:
        bot.send_message(chat_id=chat_id, text="Deze plek bestaat niet, sorry.")
        return

    # get token for Darksky
    with open('darkskytoken.txt') as file:
        token = file.readline().strip()

    URL = (DARKYSKY + "/" + token + "/" + str(location.latitude)
           + "," + str(location.longitude) + '?lang=nl&units=si')


    # print(URL)

    response = requests.get(URL)

    out = format_weather(location, response.json())

    update.message.reply_text('Hallo!\n\n' + out)

def format_weather(location, response):
    # print(response)

    maxTemp = response['daily']['data'][0]['apparentTemperatureHigh']
    minTemp = response['daily']['data'][0]['apparentTemperatureLow']
    regenKans = response['daily']['data'][0]['precipProbability']*100
    s = ''
    s += 'Locatie: ' + str(location) + '\n\n'
    s += (response['daily']['summary'] + ' ' +
          response['daily']['data'][0]['summary'] + '\n\n')
    s += ('Maximum Temperatuur: ' + str(maxTemp) + ' °C\n'
          + 'Minimum Temperatuur: ' + str(minTemp) + ' °C')

    if response['daily']['data'][0]['precipType'] == 'rain':
         s += ('\nRegenkans: ' +
               str(regenKans) + '%\n\n')

    # kleding advies:

    Temp = (maxTemp + minTemp)/2
    s += "Kledingadvies: \n" + clothing_advice(Temp, regenKans)

    return s

def clothing_advice(temperature, regenkans):
    """ adapted from https://www.moetikeenjasaan.nl """
    if regenkans > 70.0:
        if temperature < 9:
            return 'Winterjas'
        elif temperature < 15:
            return 'Dunne regenjas'
        elif temperature < 19:
            return 'Regenjas'
        elif temperature < 26:
            return 'T-shirt aan maar wel paraplu mee';
        return 'Het is zo warm, een verfrissende bui kan geen kwaad'
    else:
        if temperature < 9:
            return 'Winterjas'
        elif temperature < 15:
            return 'Dikke trui'
        elif temperature < 19:
            return 'Dunne trui of een t-shirt met lange mouwen'
        elif temperature < 26:
            return 'T-shirt'

        return 'zo weinig mogelijk kleren lol'

def get_news(bot, update):
    """ https://pythonhosted.org/feedparser/introduction.html"""

    times_parsed = [[]]*len(FEEDS)
    publish_times = set()

    # get the oldest pubdate of each RSS feed
    for i, feed in enumerate(FEEDS):

        try:
            fd = feedparser.parse(FEEDS[feed])
            # print(fd.status)

            for entry in fd.entries:
                publish_times.add(entry.published_parsed)

            times_parsed[i] = min(publish_times)

            print(f"RSS feed {feed} is {len(fd.entries)} long.")

        except Exception as e:
            print(e)

    # keep reading feeds
    for i, feed in enumerate(FEEDS):

        # get the feed and update the pub time
        pud_dates[i] = get_feed(bot, update, FEEDS[feed],
                                times_parsed[i])

    print(f"sleeping {UPDATE_FREQ}")
    time.sleep(UPDATE_FREQ)

def get_feed(bot, update, feedlink, pub_time):
    """ returns the new article of a given rss feed with a etag and modified tag """

    newfound = False

    try:

        feed = feedparser.parse(feedlink)
        # print(feed.status)

        # loop over the feed
        for entry in feed.entries:

            # skip if entry is before last pubdate
            if entry.published_parsed > pub_time:

                newfound = True
                out = format_rss(entry)

                # output
                update.message.reply_text(f"{out}", parse_mode='markdown',
                                          disable_web_page_preview=True)

            else:
                continue

            time.sleep(1)

            # grab the last published time
            pubdate = entry.published_parsed

        if not newfound:
            print('geen nieuwe artikelen bij deze check.')

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

# TODO: make why function
def why(bot, update):

    # open file pak een random reden
    with open('redenen.txt') as file:
        lines = file.readlines()
        t = random.choice(lines)

    update.message.reply_text(t)

    pass

def main():
    """ Create the Updater and pass it your bot's token. """

    # token is in other file for security
    with open('telegramtoken.txt') as file:
        t = file.readline().strip()

    updater = Updater(token=t)
    dp = updater.dispatcher

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

    dp.add_handler(CommandHandler('feeds', view_feeds))
    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(CommandHandler('hallo', hello))
    dp.add_handler(CommandHandler('news', get_news))
    dp.add_handler(CommandHandler('waarom', why))
    dp.add_handler(CommandHandler('weer', weather))



    # updater.add_error_handler(error)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
