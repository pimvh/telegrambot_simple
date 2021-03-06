"""
The module defines constants used by the Telegram bot.
"""

import json
import os

DIR = os.path.dirname(__file__)

# character typingspeed per second
HUMAN_DELAY = (1/9)

""" *** Constant URLs *** """
REDDIT = {"r/me_irl": "https://reddit.com/r/me_irl/top/.rss",
          "r/ik_ihe": "https://reddit.com/r/ik_ihe/top/.rss",
          #"r/toomeirlformeirl": "https://www.reddit.com/r/TooMeIrlForMeIrl/top/.rss"
          }

DARKSKY = "https://api.darksky.net/forecast"

NEWS_FEEDS = {"Volkskrant": "https://www.volkskrant.nl/voorpagina/rss.xml",
              "Trouw": "https://www.trouw.nl/voorpagina/rss.xml"
              #"NRC": "https://www.nrc.nl/rss/"
              }

""" *** File to pull random reasons from *** """
REASONS = os.path.join(DIR, 'redenen.txt')

""" *** Tokens for authentication *** """
TOKENS_FILE = os.path.join(DIR, 'tokens', 'tokens.json')

with open(TOKENS_FILE) as f:
    TOKENS = json.load(f)

TELEGRAM_TOKEN = TOKENS["TELEGRAM_TOKEN"]
DARKSKY_TOKEN = TOKENS["DARKSKY_TOKEN"]
ADMIN = TOKENS["ADMIN"]
PYMONGO = TOKENS["DATABASE_URI"]
