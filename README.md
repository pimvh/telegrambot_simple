# telegrambot_simple
Implements a simple telegram bot based using the  python-telegram-bot wrapper.
It responses are written in Dutch, but its in code in English for accessibility.

The module below implements a telegram bot with a number of Command Handlers:
- /help: help (displays a help message)
- /hallo: responds to the user
- /weer: weather (returns the weather at given place using DARKSY)
- /waarom: a why function returns random reasons to the user to answer
- /nieuws: a news function (still developing, outputs RRS feed data from newspapers to a Telegramgroup
- /feeds: displays the feeds currently accessed by this bot
