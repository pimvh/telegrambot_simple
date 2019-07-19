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
import operator
import pickle
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
                          Filters, PicklePersistence,
                          MessageHandler)
import telegram.ext

# Token filename
TELEGRAM_TOKEN = "tokens/token_telegram_API.txt"

# Weather API tokenfile, URL
DARKYSKY = "https://api.darksky.net/forecast"
DARKSKY_TOKEN = "tokens/token_DARKSKY_API.txt"

# Admin
ADMIN = "ADMIN.txt"

# Conversation states
CHOICE, UPDATE = range(2)

# Pickle file
pickle_file = "bierlijst.pickle"

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

def beer_start(update, context):
    """ starts the beer conversation, replying a keyboard with options"""
    chat_id = update.message.chat_id
    bot = context.bot

    reply_keyboard = [["Krijgen" , "Geven", "Nog te krijgen?", "Nog te geven?"]]
    msg = emoji.emojize(":beer:")
    msg += " Geef aan wat je wilt! "
    msg += emoji.emojize(":beer:")

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

        msg = beer_output_data(chat_id, text)
        bot.send_message(chat_id=chat_id, text=msg,
                         parse_mode=telegram.ParseMode.MARKDOWN,
                         reply_markup=ReplyKeyboardRemove())

        return ConversationHandler.END

    elif text == "Krijgen" or text == "Geven":

        msg = "Geef de naam van de persoon en het aantal."

        context.user_data["choice"] = text

        bot.send_message(chat_id=chat_id, text=msg,
                         parse_mode=telegram.ParseMode.MARKDOWN,
                         reply_markup=ReplyKeyboardRemove())

        return UPDATE

    else:
        msg = "Sorry, maar dit kan niet."
        bot.send_message(chat_id=chat_id, text=msg,
                         parse_mode=telegram.ParseMode.MARKDOWN)

        return ConversationHandler.END

def beer_update(update, context):

    chat_id = update.message.chat_id
    bot = context.bot
    text = update.message.text

    choice = context.user_data["choice"]
    del context.user_data["choice"]

    try:
        arg = text.split(" ")

        if len(arg) == 2:
            name, number = arg
            name.capwords()
            opt = None
        else:
            name, number, opt = arg

        assert(number.isdigit())
        # print(name, number, opt)

    except:
        msg = "Sorry, maar dit kan niet."
        bot.send_message(chat_id=chat_id, text=msg,
                         parse_mode=telegram.ParseMode.MARKDOWN)

        return ConversationHandler.END

    myclient = pymongo.MongoClient()
    beer_base = myclient["beerbase"][str(chat_id)]
    query = {"name": name}

    out = beer_base.find_one(query)

    # check if exist in database, if not
    if out is None and opt is None:
        entry = {"type": choice, "name": name, "number": number}
        beer_base.insert_one(entry)

        msg = "Top, toegevoegd."

    else:
        # if it does check whether operator was given
        if opt is None:
            msg = "Staat al in de database, geef me een optie (+ of -)."

        elif opt == '+' or opt == '-':
            operators = { "+": operator.add, "-": operator.sub }
            new_num = operators[opt](int(out["number"]), int(number))

            if new_num <= 0:
                beer_base.delete_one(query)
                msg = "Je krijgt geen bier meer van *" + name + "*."
            else:

                # update entry
                update_entry = {"type": choice, "name": name,
                                "number": str(new_num)}
                beer_base.update(query, update_entry)

                msg = ("Geupdate, Je krijgt " + str(new_num) + " " +
                      str(emoji.emojize(":beer:")) + " van" +
                      " *" + name + "*.\n")
        else:
            msg = "Sorry, maar dit kan niet."

    bot.send_message(chat_id=chat_id, text=msg,
                     parse_mode=telegram.ParseMode.MARKDOWN)

    return ConversationHandler.END

def beer_output_data(chat_id, key):

    if "krijgen" in key:
        key = "Krijgen"
    else:
        key = "Geven"

    myclient = pymongo.MongoClient()
    beer_base = myclient["beerbase"][str(chat_id)]
    query = {"type": key}
    # query
    out = beer_base.find_one(query)

    if out is None and key == "Krijgen":
        s = "Je krijgt bier van niemand helaas. Mag wel."
    elif out is None and key == "Geven":
        s = "Je hoeft geen bier aan iemand te geven. Mag wel."

    else:
        out = beer_base.find(query)
        s = ""
        # print(out)

        for elem in out:

            # print(elem)

            if key == "Krijgen":
                s += ("Je krijgt " + elem['number'] + " " +
                      str(emoji.emojize(":beer:")) + " van" +
                      " *" + elem['name'] + "*.\n")
            if key == "Geven":
                s += ("Je bent " + elem['number'] + " " +
                      str(emoji.emojize(":beer:")) + " verschuldigd aan" +
                      " *" + elem['name'] + "*.\n")

    return s

def done(update, context):

    bot = context.bot
    user = update.message.from_user

    if "choice" in context.user_data:
        del context.user_data["choice"]

    msg = "Joe! Dank voor de input!"
    bot.send_message(chat_id=update.message.chat_id, text=msg,
                     parse_mode=telegram.ParseMode.MARKDOWN,
                     reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END

def weather(update, context):
    chat_id = update.message.chat_id
    bot = context.bot

    #board = ["Amsterdam","Anders"]
    # kb = [[telegram.KeyboardButton("Amsterdam")]]
    # kb, one_time_keyboard=True

    # reply_markup=kb_markup

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
    mes = "This bot pulls from the following feeds: "
    update.message.reply_text(mes + f"\n {FEEDS.keys()}")

def why(update, context):

    bot = context.bot
    # return a random reason from file
    with open("redenen.txt") as file:
        lines = file.readlines()
        t = random.choice(lines)

        bot.send_message(chat_id=update.message.chat_id, text=t,
                         parse_mode=telegram.ParseMode.MARKDOWN)

def main():
    """ Create the updater and pass it your bot"s token
        and add the handlers to the bot. """

    # token is in other file for security
    with open(TELEGRAM_TOKEN) as file:
        t = file.readline().strip()

    with open(ADMIN) as file:
        admin = file.readline().strip()

    # pp = PicklePersistence(filename="bierlijst.pickle")
    updater = Updater(token=t, use_context=True) # persistence=pp,

    dp = updater.dispatcher

    # log errors
    logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                        level=logging.INFO)

    beer_conv = ConversationHandler(
                    entry_points=[CommandHandler("bier", beer_start)],
                    states={
                        CHOICE: [MessageHandler(Filters.text, beer_choice)],
                        UPDATE: [MessageHandler(Filters.text, beer_update)],
                    },

                    fallbacks=[CommandHandler("klaar", done)],

                    name="Bierversatie",
                    # per_user=True,
                    # persistent=True
    )
    dp.add_handler(beer_conv)

    dp.add_handler(CommandHandler("feeds", view_feeds))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("hallo", hello))
    dp.add_handler(CommandHandler("news", news, filters=Filters.user(username=admin)))
    dp.add_handler(CommandHandler("waarom", why))
    dp.add_handler(CommandHandler("weer", weather))


    # updater.add_error_handler(error)
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
