import requests

from geopy.geocoders import Nominatim
from operator import itemgetter
import emoji

from telegram import ParseMode
from telegram.ext import CommandHandler

from constants import DARKSKY_TOKEN, DARKSKY

def get_weather(update, context):
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

    try:
        location = geolocator.geocode(location_str)
    except:
        bot.send_message(chat_id=chat_id,
                         text="De Geolocator service doet het ff niet, zoek maar op een normale plek het weer op.")

    if location is None:
        bot.send_message(chat_id=chat_id, text="Deze plek bestaat niet, sorry.")
        return

    URL = (DARKSKY + "/" + DARKSKY_TOKEN + "/" + str(location.latitude)
           + "," + str(location.longitude) + "?lang=nl&units=si")
    response = requests.get(URL)

    if response is None:
        bot.send_message(chat_id=chat_id, text="Kan niet verbinden met API.")
    out = format_weather(location, response.json())

    bot.send_message(chat_id=update.message.chat_id,
                     text=out,
                     parse_mode=ParseMode.MARKDOWN)

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

    s += weather_icon_helper(daily.get("icon")) + "\n\n"

    if (daily_data.get("moonPhase")):
        s += "Maanstand: " + moonphase_icon_helper(daily_data.get("moonPhase")) + "\n\n"

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

def weather_icon_helper(s):
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

def moonphase_icon_helper(s):
    lumination_num = float(s)
    phase_num = [0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1]
    moon_phase_emojis =[":new_moon:", "waxing_crescent_moon:",
                        ":first_quarter_moon:", ":waxing_gibbous_moon:",
                        ":full_moon:", ":waning_gibbous_moon:",
                        ":last_quarter_moon:", ":waning_crescent_moon:",
                        ":new_moon:"]

    dist = [abs(lumination_num - num) for num in phase_num]
    min_index = min(enumerate(dist), key=itemgetter(1))[0]

    return emoji.emojize(moon_phase_emojis[min_index])

weer = CommandHandler("weer", get_weather)
