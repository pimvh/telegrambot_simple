import emoji
import pymongo

from telegram import ParseMode, ReplyKeyboardMarkup, ReplyKeyboardRemove

from telegram.ext import CommandHandler
from telegram.ext import ConversationHandler
from telegram.ext import MessageHandler
from telegram.ext import (BaseFilter, Filters)

# Conversation states
CHOICE, NAME, UPDATE = range(3)

def beer_start(update, context):
    """ starts the beer conversation, replying a keyboard with options"""
    chat_id = update.message.chat_id
    bot = context.bot

    reply_keyboard = [["Krijgen van" , "Geven aan", "Nog te krijgen?", "Nog te geven?"]]
    msg = emoji.emojize(":beer_mug: Geef aan wat je wilt! :beer_mug:")

    bot.send_message(chat_id=chat_id, text=msg,
                     parse_mode=ParseMode.MARKDOWN,
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
                         parse_mode=ParseMode.MARKDOWN,
                         reply_markup=ReplyKeyboardRemove())

        return ConversationHandler.END

    elif text == "Krijgen van" or text == "Geven aan":

        msg = "Geef de naam van de persoon."

        context.user_data["choice"] = text[0]

        bot.send_message(chat_id=chat_id, text=msg,
                         parse_mode=ParseMode.MARKDOWN,
                         reply_markup=ReplyKeyboardRemove())

        return NAME

    else:
        msg = "Sorry, maar dit kan niet."
        bot.send_message(chat_id=chat_id, text=msg,
                         parse_mode=ParseMode.MARKDOWN)

        return ConversationHandler.END

def beer_name(update, context):
    chat_id = update.message.chat_id
    bot = context.bot
    text = update.message.text

    context.user_data["name"] = text.capitalize()

    reply_keyboard = [["1", "2", "3", "4", "5"]]
    msg = "Hoeveel?"

    bot.send_message(chat_id=chat_id, text=msg,
                     parse_mode=ParseMode.MARKDOWN,
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
                         parse_mode=ParseMode.MARKDOWN,
                         reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    choice = context.user_data["choice"]
    del context.user_data["choice"]

    name = context.user_data["name"]
    del context.user_data["name"]

    myclient = pymongo.MongoClient()
    beer_database = myclient["beerbase"][str(chat_id)]
    query = {"name": name}

    out = beer_database.find_one(query)

    if choice == "G":
        number*=-1

    if beer_database.count_documents({}) > 10:
        msg = "Maat fix ff een andere plek om je bieries bij te houden, niet mijn server volgooien aub."
        bot.send_message(chat_id=chat_id, text=msg,
                         parse_mode=ParseMode.MARKDOWN,
                         reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    # check if exist in database, if not add
    if out is None:

        entry = {"name": name, "number": number}
        beer_database.insert_one(entry)

        msg = f"{name} stond nog niet in de database, ik heb deze persoon toegevoegd.\n"

    # else the name is in there
    else:
        # calculate new number

        new_num = out["number"] + number

        # print(out["number"], number, new_num)
        if new_num > 0:
            # update entry
            update_entry = {"name": name, "number": new_num}
            beer_database.update(query, update_entry)

            msg = emoji.emojize(f"Geupdate, nu {str(new_num)} :beer_mug: bij *{name}*.")

        elif new_num == 0:
            beer_database.delete_one(query)

            msg = f"{name} staat nu niet meer in de database."

        else:
            # swap the choices

            # update entry
            update_entry = {"name": name, "number": new_num}
            beer_database.update(query, update_entry)

            msg = emoji.emojize(f"Geupdate, nu {str(new_num)} :beer_mug: bij *{name}*.")

    bot.send_message(chat_id=chat_id, text=msg,
                     parse_mode=ParseMode.MARKDOWN,
                     reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END

def beer_output_data(chat_id, key):

    myclient = pymongo.MongoClient()
    beer_database = myclient["beerbase"][str(chat_id)]
    krijgen = False

    if key == 'k':
        query = { "number": {"$gt": 0 } }
        krijgen = True
    else:
        query = { "number": {"$lt": 0 } }

    # count docs
    item_count = beer_database.count_documents(query)
    # print('this is the item count', item_count)
    s=""

    if item_count == 0:
        if krijgen:
            s = "Je krijgt bier van niemand helaas. Mag wel (:"
        else:
            s = "Je hoeft geen bier aan iemand te geven. Mag wel (:"
    else:
        # query the database
        out = beer_database.find(query)

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
                     parse_mode=ParseMode.MARKDOWN,
                     reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END

beer_conv = ConversationHandler(
                entry_points=[CommandHandler("bier", beer_start)],
                states={
                    CHOICE: [MessageHandler(Filters.text, beer_choice)],
                    NAME: [MessageHandler(Filters.text, beer_name)],
                    UPDATE: [MessageHandler(Filters.text, beer_update)],
                },

                fallbacks=[CommandHandler("klaar", beer_end)],
                name="Bierversatie", )
