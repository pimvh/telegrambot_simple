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
import emoji
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
def start(update, context):
    help(update, context)

def help(update, context):
    """ displays a help message (Dutch) """

    msg = """ Deze bot heeft de volgende *commandos*:
    - /help : laat dit bericht zien
    - /weer _[locatie]_ : geeft weer terug op locatie
    - /hallo : krijg een groet van deze bot
    - /waarom : krijg een willekeurige reden terug
    """
    update.send_message(chat_id=context.message.chat_id, text=msg,
                     parse_mode=telegram.ParseMode.MARKDOWN)

def hello(update, context):
    telegram_user = context.message.from_user
    context.message.reply_text(f"Hallo {telegram_user.first_name}!")

    # bot.send_message(chat_id=update.message.chat_id,
    #              text="*bold* _italic_ `fixed width font` [link](http://google.com).",
    #              parse_mode=telegram.ParseMode.MARKDOWN)

def weather(update, context):
    chat_id = context.message.chat_id

    #board = ['Amsterdam','Anders']
    # kb = [[telegram.KeyboardButton('Amsterdam')]]
    # kb, one_time_keyboard=True

    # reply_markup=kb_markup

    try:
        location_str = context.args
        assert(location_str, str)

    except:
        update.send_message(chat_id=chat_id, text="Geen locatie gegeven. Standaard: Amsterdam")
        location_str = "Amsterdam"

    # get coordinates for DARKSKY based on string
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
    response = requests.get(URL)
    out = format_weather(location, response.json())

    update.send_message(chat_id=context.message.chat_id,
                     text=out,
                     parse_mode=telegram.ParseMode.MARKDOWN)

def format_weather(location, response):
    """ pulls wanted variables from JASON-object return by the DARK-SKY API,
        gives back formatted string (Dutch)"""

    maxTemp = response['daily']['data'][0]['apparentTemperatureHigh']
    minTemp = response['daily']['data'][0]['apparentTemperatureLow']
    precipProb = response['daily']['data'][0]['precipProbability']*100
    precipType = response['daily']['data'][0]['precipType']
    precipIntensity = response['daily']['data'][0]['precipIntensity']

    s = ''
    s += 'Locatie: ' + str(location) + '\n\n'
    s += (response['daily']['summary'] + ' ' +
          response['daily']['data'][0]['summary'] + '\n\n')

    s += icon_helper(response['daily']['icon']) + '\n\n'

    s += ('Maximum Temperatuur: ' + str(maxTemp) + ' °C\n'
          + 'Minimum Temperatuur: ' + str(minTemp) + ' °C')

    if precipIntensity:

        if  precipType == 'rain':
            s += '\nRegenkans: '
        elif precipType == 'snow':
            s += '\nSneeuwkans: '
        elif precipType == 'sleet':
            s += '\nHagelkans: '

        s += str(precipProb) + '%\n\n'

    # take avarage temp for day
    Temp = (maxTemp + minTemp)/2

    # prevent errors
    if precipIntensity == None:
        precipIntensity = 0

    s += 'Kledingadvies: \n' + clothing_advice(Temp, precipProb, precipIntensity)

    return s

def clothing_advice(temperature, precipProb, precipIntensity):
    """ adapted from https://www.moetikeenjasaan.nl
        gives clothing advice based on precipation (Dutch)"""
    if precipProb > 70.0 or precipIntensity > 0.05:
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

def icon_helper(s):
    """ returns the appropriate emoticon for a weather condition """

    # using emoji package to convert string to unicode
    return {
        "clear-day" : emoji.emojize(":sunny:"),
         "clear-night" : emoji.emojize(":full_moon:"),
         "rain" : emoji.emojize(":cloud_with_rain:"),
         "snow" : emoji.emojize(":cloud_with_snow: "),
         "sleet" : emoji.emojize(":cloud_with_snow:"),
         "wind" : emoji.emojize(":wind_blowing_face:"),
         "fog" : emoji.emojize(":fog:"),
         "cloudy" : emoji.emojize(":cloud:"),
         "partly-cloudy-day" : emoji.emojize(":white_sun_with_small_cloud:"),
         "partly-cloudy-night" : emoji.emojize(":white_sun_behind_cloud:")
    }.get(s, emoji.emojize(":earth_africa:"))


# TODO: finish news function
def get_news(update, context):
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
        pud_dates[i] = get_feed(update, context, FEEDS[feed],
                                times_parsed[i])

    print(f"sleeping {UPDATE_FREQ}")
    time.sleep(UPDATE_FREQ)

# TODO: see above, finish news function
def get_feed(update, context, feedlink, pub_time):
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

def view_feeds(update, context):
    mes = "This bot pulls from the following feeds: "
    update.message.reply_text(mes + f"\n {FEEDS.keys()}")

def why(update, context):

    # return a random reason from file
    with open('redenen.txt') as file:
        lines = file.readlines()
        t = random.choice(lines)

    context.message.reply_text(t)

def main():
    """ Create the updater and pass it your bot's token
        and add the handlers to the bot. """

    # token is in other file for security
    with open('telegramtoken.txt') as file:
        t = file.readline().strip()

    updater = Updater(token=t)
    dp = updater.dispatcher

    # log errors
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
