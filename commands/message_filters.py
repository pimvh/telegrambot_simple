import re

from telegram.ext import (BaseFilter, Filters)

class HelloFilter(BaseFilter):
    def filter(self, message):
        return re.search(r'(hallo|hoi)(\?|!|\.| |)*', message.text, re.I)

hello_filter = HelloFilter()

class LeukFilter(BaseFilter):
    def filter(self, message):
        # TODO: filter fixen
        return re.search(r'leuk(\?|!|\.| |)*', message.text, re.I)

leuk_filter = LeukFilter()

class QuestionFilter(BaseFilter):
    def filter(self, message):
        msg = str.lower(message.text)
        return ('waarom' in msg or '?' in msg) and not 'https' in msg

question_filter = QuestionFilter()

class YourMomFilter(BaseFilter):
    def filter(self, message):
        msg = str.lower(message.text)
        return 'mama' in msg or 'moeder' in msg

yourmom_filter = YourMomFilter()
