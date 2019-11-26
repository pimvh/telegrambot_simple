import feedparser
import collections

from telegram.ext import CommandHandler
from telegram.ext import BaseFilter, Filters

from constants import ADMIN

from telegram.ext import BaseFilter, Filters
from telegram.ext import CommandHandler

# Newsfeed update interval
TIMED_INTERVAL = 900

# links of feeds to output
NEWS_FEEDS = {
"Volkskrant": "https://www.volkskrant.nl/voorpagina/rss.xml",
"Trouw": "https://www.trouw.nl/voorpagina/rss.xml"
# "NRC": "https://www.nrc.nl/rss/",
}

def news(context):
    """https://pythonhosted.org/feedparser/introduction.html"""

    saved_titles = [collections.deque(maxlen=50) for i in range(len(NEWS_FEEDS))]

    context.job.run_repeating(get_news_rep, interval= TIMED_INTERVAL, first=0,
                            context=saved_titles)

def get_news_rep(context):

    bot = context.bot
    queue_titles_list = job.context
    # get the oldest pubdate of each RSS feed
    for i, feed in enumerate(NEWS_FEEDS):

        queue_titles = queue_titles_list[i]

        try:

            fd = feedparser.parse(NEWS_FEEDS[feed])

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
    mes = f"This bot pulls from the following feeds:\n{NEWS_FEEDS.keys()} "
    update.message.reply_text(mes)

view_feeds = CommandHandler("feeds", view_feeds)
news = CommandHandler("news", news, filters=Filters.user(username=ADMIN))
