#!/usr/bin/env python3

"""
The module below implements a telegram bot with a number of commandhandlers:
- a weather lookup function
- a why function returns random reasons to the user
"""

__author__ = """Pim van Helvoirt"""
__copyright__ = "None"
__credits__ = [""]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "None"
__email__ = "pim.van.helvoirt@home.nl"
__status__ = "Production"

import collections
import datetime
import emoji
import feedparser
from functools import wraps
import logging
import os
import pymongo
import random
import requests
import sys
import time

# geolocation lib
from geopy.geocoders import Nominatim

# telegram python wrapper
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, ConversationHandler,
                          BaseFilter, Filters, MessageHandler)
import telegram.ext

# get the correct DIR
DIR = os.path.dirname(__file__)

# Token filename
TELEGRAM_TOKEN = os.path.join(DIR, 'tokens', 'token_telegram_API.txt')

# Weather API tokenfile, URL
DARKYSKY = "https://api.darksky.net/forecast"
DARKSKY_TOKEN = os.path.join(DIR, 'tokens', 'token_DARKSKY_API.txt')

# Reasons
REASONS = os.path.join(DIR, 'redenen.txt')

# Admin
ADMIN = os.path.join(DIR, 'ADMIN.txt')

# Conversation states
CHOICE, NAME, UPDATE = range(3)

# Newsfeed update interval
TIMED_INTERVAL = 900

# links of feeds to output
FEEDS = {
"Volkskrant": "https://www.volkskrant.nl/voorpagina/rss.xml",
"Trouw": "https://www.trouw.nl/voorpagina/rss.xml"
# "NRC": "https://www.nrc.nl/rss/",
}

def start(update, context):
    # help(update, context)
    pass

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

def hello(update, context):
    chat_id = update.message.chat_id
    user = update.message.from_user
    bot = context.bot

    bot.send_message(chat_id=chat_id, text=f"Hallo {user.first_name}!")

def why(update, context):

    bot = context.bot
    # return a random reason from file
    with open(REASONS) as file:
        lines = file.readlines()
        t = random.choice(lines)

        bot.send_message(chat_id=update.message.chat_id, text=t,
                         parse_mode=telegram.ParseMode.MARKDOWN)

def leuk(update, context):
    chat_id = update.message.chat_id
    user = update.message.from_user
    bot = context.bot

    bot.send_message(chat_id=chat_id, text=f"Je bent zelf leuk {user.first_name}!")

def beer_start(update, context):
    """ starts the beer conversation, replying a keyboard with options"""
    chat_id = update.message.chat_id
    bot = context.bot

    reply_keyboard = [["Krijgen van" , "Geven aan", "Nog te krijgen?", "Nog te geven?"]]
    msg = emoji.emojize(":beer_mug: Geef aan wat je wilt! :beer_mug:")

    bot.send_message(chat_id=chat_id, text=msg,
                     parse_mode=telegram.ParseMode.MARKDOWN,
                     reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                      one_time_keyboard=True))
    return CHOICE

def beer_choice(update, context):
    """ based on user input from the reply keyboard,
        gives either output from the mongodb or lets the user change entries """
    chat_id = update.message.chat_id
    bot = context.bot
    text = update.message.text

    if text == "Nog te krijgen?" or text == "Nog te geven?":

        msg = beer_output_data(chat_id, text[7])
        bot.send_message(chat_id=chat_id, text=msg,
                         parse_mode=telegram.ParseMode.MARKDOWN,
                         reply_markup=ReplyKeyboardRemove())

        return ConversationHandler.END

    elif text == "Krijgen van" or text == "Geven aan":

        msg = "Geef de naam van de persoon."

        context.user_data["choice"] = text[0]

        bot.send_message(chat_id=chat_id, text=msg,
                         parse_mode=telegram.ParseMode.MARKDOWN,
                         reply_markup=ReplyKeyboardRemove())

        return NAME

    else:
        msg = "Sorry, maar dit kan niet."
        bot.send_message(chat_id=chat_id, text=msg,
                         parse_mode=telegram.ParseMode.MARKDOWN)

        return ConversationHandler.END

def beer_name(update, context):
    chat_id = update.message.chat_id
    bot = context.bot
    text = update.message.text

    context.user_data["name"] = text.capitalize()

    reply_keyboard = [["1", "2", "3", "4", "5"]]
    msg = "Hoeveel?"

    bot.send_message(chat_id=chat_id, text=msg,
                     parse_mode=telegram.ParseMode.MARKDOWN,
                     reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                      one_time_keyboard=True))

    return UPDATE

def beer_update(update, context):

    chat_id = update.message.chat_id
    bot = context.bot
    text = update.message.text

    try:
        assert(text.isdigit())
        number = int(text)

    except:
        msg = "Sorry, maar dit kan niet."
        bot.send_message(chat_id=chat_id, text=msg,
                         parse_mode=telegram.ParseMode.MARKDOWN,
                         reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    choice = context.user_data["choice"]
    del context.user_data["choice"]

    name = context.user_data["name"]
    del context.user_data["name"]

    myclient = pymongo.MongoClient()
    beer_base = myclient["beerbase"][str(chat_id)]
    query = {"name": name}

    out = beer_base.find_one(query)

    if choice == "G":
        number*=-1

    if beer_base.count_documents() > 25:
        msg = "Maat fix ff een andere plek om je bieries bij te houden, niet mijn server volgooien aub."
        bot.send_message(chat_id=chat_id, text=msg,
                         parse_mode=telegram.ParseMode.MARKDOWN,
                         reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    # check if exist in database, if not add
    if out is None:

        entry = {"name": name, "number": number}
        beer_base.insert_one(entry)

        msg = f"{name} stond nog niet in de database, ik heb deze persoon toegevoegd.\n"

    # else the name is in there
    else:
        # calculate new number

        new_num = out["number"] + number

        print(out["number"], number, new_num)
        if new_num > 0:
            # update entry
            update_entry = {"name": name, "number": new_num}
            beer_base.update(query, update_entry)

            msg = emoji.emojize(f"Geupdate, nu {str(new_num)} :beer_mug: bij *{name}*.")

        elif new_num == 0:
            beer_base.delete_one(query)

            msg = f"{name} staat nu niet meer in de database."

        else:
            # swap the choices

            # update entry
            update_entry = {"name": name, "number": new_num}
            beer_base.update(query, update_entry)

            msg = emoji.emojize(f"Geupdate, nu {str(new_num)} :beer_mug: bij *{name}*.")

    bot.send_message(chat_id=chat_id, text=msg,
                     parse_mode=telegram.ParseMode.MARKDOWN,
                     reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END

def beer_output_data(chat_id, key):

    myclient = pymongo.MongoClient()
    beer_base = myclient["beerbase"][str(chat_id)]
    krijgen = False

    if key == 'k':
        query = { "number": {"$gt": 0 } }
        krijgen = True
    else:
        query = { "number": {"$lt": 0 } }

    # count docs
    item_count = beer_base.count_documents(query)
    # print('this is the item count', item_count)
    s=""

    if item_count == 0:
        if krijgen:
            s = "Je krijgt bier van niemand helaas. Mag wel (:"
        else:
            s = "Je hoeft geen bier aan iemand te geven. Mag wel (:"
    else:
        # query the database
        out = beer_base.find(query)

        for elem in out:

            if krijgen:
                s += emoji.emojize(f"Je krijgt {elem['number']} :clinking_beer_mugs: van *{elem['name']}*.\n")
            else:
                s += emoji.emojize(f"Je bent {abs(elem['number'])} :clinking_beer_mugs: verschuldigd aan *{elem['name']}*.\n")

    return s

def beer_end(update, context):

    bot = context.bot
    user = update.message.from_user

    if "choice" in context.user_data:
        del context.user_data["choice"]

    if "name" in context.user_data:
        del context.user_data["name"]

    msg = "Joe! Dank voor de input!"
    bot.send_message(chat_id=update.message.chat_id, text=msg,
                     parse_mode=telegram.ParseMode.MARKDOWN,
                     reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END

def weather(update, context):
    chat_id = update.message.chat_id
    bot = context.bot

    try:
        location_str = context.args[0]

    except:
        bot.send_message(chat_id=chat_id,
                         text="Geen geldige/lege query. Standaard: Amsterdam")

        location_str = "Amsterdam"

    # get coordinates for DARKSKY based on string
    geolocator = Nominatim()
    location = geolocator.geocode(location_str)

    if location is None:
        bot.send_message(chat_id=chat_id, text="Deze plek bestaat niet, sorry.")
        return

    # get token for Darksky
    with open(DARKSKY_TOKEN) as file:
        token = file.readline().strip()

    URL = (DARKYSKY + "/" + token + "/" + str(location.latitude)
           + "," + str(location.longitude) + "?lang=nl&units=si")
    response = requests.get(URL)

    if response is None:
        bot.send_message(chat_id=chat_id, text="Kan niet verbinden met API.")
    out = format_weather(location, response.json())

    bot.send_message(chat_id=update.message.chat_id,
                     text=out,
                     parse_mode=telegram.ParseMode.MARKDOWN)

def format_weather(location, response):
    """ pulls wanted variables from JSON-object return by the DARK-SKY API,
        gives back formatted string (Dutch)"""

    try:
        daily = response.get("daily")
        daily_data = daily.get("data")[0]

    except KeyError as e:
        return ""
    except IndexError as e:
        return ""

    maxTemp = daily_data.get("apparentTemperatureHigh")
    minTemp = daily_data.get("apparentTemperatureLow")

    precipProb = daily_data.get("precipProbability")
    precipType = daily_data.get("precipType")
    precipIntensity = daily_data.get("precipIntensity")

    # prevent errors
    if not precipIntensity:
        precipIntensity = 0

    if precipProb:
        precipProb *= 100

    s = ""
    s += "Locatie: " + str(location) + "\n\n"
    s += (daily.get("summary") + " " +
          daily_data.get("summary") + "\n\n")

    s += icon_helper(daily.get("icon")) + "\n\n"

    s += ("Maximum Temperatuur: " + str(maxTemp) + " °C\n"
          + "Minimum Temperatuur: " + str(minTemp) + " °C\n\n")

    if precipType:

        if  precipType == "rain":
            s += "\nRegenkans: "
        elif precipType == "snow":
            s += "\nSneeuwkans: "
        elif precipType == "sleet":
            s += "\nHagelkans: "

        s += str(precipProb) + "%\n\n"

    # take avarage temp for day
    Temp = (maxTemp + minTemp)/2
    s += "Kledingadvies: \n" + clothing_advice(Temp, precipProb, precipIntensity)

    return s

def clothing_advice(temperature, precipProb, precipIntensity):
    """ adapted from https://www.moetikeenjasaan.nl
        gives clothing advice based on precipation (Dutch)"""
    if precipProb > 70.0 or precipIntensity > 0.05:
        if temperature < 9:
            return "Winterjas"
        elif temperature < 15:
            return "Dunne regenjas"
        elif temperature < 19:
            return "Regenjas"
        elif temperature < 26:
            return "T-shirt aan maar wel paraplu mee";
        return "Het is zo warm, een verfrissende bui kan geen kwaad"
    else:
        if temperature < 9:
            return "Winterjas"
        elif temperature < 15:
            return "Dikke trui"
        elif temperature < 19:
            return "Dunne trui of een t-shirt met lange mouwen"
        elif temperature < 26:
            return "T-shirt"

        return "zo weinig mogelijk kleren lol"

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

def news(context):
    """ https://pythonhosted.org/feedparser/introduction.html"""

    saved_titles = [collections.deque(maxlen=50) for i in range(len(FEEDS))]

    context.job.run_repeating(get_news_rep, interval= TIMED_INTERVAL, first=0,
                            context=saved_titles)

def get_news_rep(context):

    bot = context.bot
    queue_titles_list = job.context
    # get the oldest pubdate of each RSS feed
    for i, feed in enumerate(FEEDS):

        queue_titles = queue_titles_list[i]

        try:

            fd = feedparser.parse(FEEDS[feed])

            i = 0
            # loop over the feed
            for entry in fd.entries:

                # print(i)
                i+=1

                if entry.title in queue_titles:
                    continue

                # print(entry.title)
                queue_titles.appendleft(entry.title)

                out = format_rss(feed, entry)
                # print(out)

                update.send_message(chat_id="@dutch_news", text=out,
                                    disable_web_page_preview=True,
                                    parse_mode=telegram.ParseMode.MARKDOWN)

        except Exception as e:
            print(e)

def format_rss(feed, text):
    """ does some nice markup for the RSS feed """
    s = ""
    s += ("*" + feed + text.title + "*" + "\n\n" + text.summary + "\n\n" +
         text.link)
    return s

def view_feeds(update, context):
    mes = f"This bot pulls from the following feeds:\n{FEEDS.keys()} "
    update.message.reply_text(mes)

def main():
    """ Create the updater and pass it your bot"s token
        and add the handlers to the bot. """

    # token is in other file for security
    with open(TELEGRAM_TOKEN) as file:
        t = file.readline().strip()

    with open(ADMIN) as file:
        admin = file.readline().strip()

    updater = Updater(token=t, use_context=True)

    dp = updater.dispatcher

    # log errors
    logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                        level=logging.INFO)

    beer_conv = ConversationHandler(
                    entry_points=[CommandHandler("bier", beer_start)],
                    states={
                        CHOICE: [MessageHandler(Filters.text, beer_choice)],
                        NAME: [MessageHandler(Filters.text, beer_name)],
                        UPDATE: [MessageHandler(Filters.text, beer_update)],
                    },

                    fallbacks=[CommandHandler("klaar", beer_end)],

                    name="Bierversatie",
                    # per_user=True,
    )

    dp.add_handler(beer_conv)
    dp.add_handler(CommandHandler("feeds", view_feeds))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("hallo", hello))
    dp.add_handler(CommandHandler("news", news, filters=Filters.user(username=admin)))
    dp.add_handler(CommandHandler("waarom", why))
    dp.add_handler(CommandHandler("weer", weather))

    dp.add_handler(MessageHandler(leuk_filter, leuk))

    # updater.add_error_handler(error)
    updater.start_polling()
    updater.idle()

class LeukFilter(BaseFilter):
    def filter(self, message):
        return 'leuk' in str.lower(message.text)

leuk_filter = LeukFilter()

if __name__ == "__main__":
    main()
