"""
This module implements filters to filter messages from the user
"""
import re

from telegram.ext import MessageFilter

class HelloFilter(MessageFilter):
    """ a message filter that filters hello, based on a regex """
    def filter(self, message):
        return re.search(r'(hallo|hoi)(\?|!|\.| |)*', message.text, re.I)

hello_filter = HelloFilter()

class LeukFilter(MessageFilter):
    """ a message filter that filters leuk, based on a regex """
    def filter(self, message):
        return re.search(r'leuk(\?|!|\.| |)*', message.text, re.I)

leuk_filter = LeukFilter()

class QuestionFilter(MessageFilter):
    """ a message filter that filters questions, based on a regex """
    def filter(self, message):
        msg = str.lower(message.text)
        return ('waarom' in msg or '?' in msg) and 'https' not in msg

question_filter = QuestionFilter()

class YourMomFilter(MessageFilter):
    """ a message filter that filters mama or moeder """
    def filter(self, message):
        msg = str.lower(message.text)
        return 'mama' in msg or 'moeder' in msg

yourmom_filter = YourMomFilter()

class HardTimesFilter(MessageFilter):
    def filter(self, message):
        return re.search(r'(moeilijk|ingewikkeld)(\?|!|\.| |)*',
                         message.text, re.I)

hardtimes_filter = HardTimesFilter()

class RedditPageFilter(MessageFilter):
    """ a message filter to filters reddit pages """
    def filter(self, message):
        return re.search(r'r/(me_irl|ik_ihe|toomeirlformeirl)',
                         message.text, re.I)

redditpage_filter = RedditPageFilter()
