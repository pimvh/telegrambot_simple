"""
The module defines constants used by the Telegram bot.
"""

import json
import os

DIR = os.path.dirname(__file__)

"""
    *** Constant URLs ***
"""
REDDIT = "https://reddit.com/r/me_irl/top/.rss"
DARKSKY = "https://api.darksky.net/forecast"

"""
    *** File to pull random reasons from ***
"""
REASONS = os.path.join(DIR, 'redenen.txt')

"""
    *** Tokens for authentication ***
"""
TOKENS_FILE = os.path.join(DIR, 'tokens', 'tokens.json')

with open(TOKENS_FILE) as f:
    TOKENS = json.load(f)

TELEGRAM_TOKEN = TOKENS["TELEGRAM_TOKEN"]
DARKSKY_TOKEN = TOKENS["DARKSKY_TOKEN"]
ADMIN = TOKENS["ADMIN"]
