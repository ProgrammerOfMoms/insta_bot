# -*- coding: utf-8 -*-
import sys
from bot import Bot

bot = Bot("your login", "your password")

actions = sys.argv[1:]
allowed_actions = []
for action in actions:
    if action == '--like':
        allowed_actions.append((bot.like,))
        continue
    elif action == '--subscribe':
        if '--fsubscribe' in actions:
            raise '--subscribe and --fsubscribe keys can not be used together'
        allowed_actions.append((bot.subscribe,))
        continue
    elif action == 'fsubscribe':
        if '--subscribe' in actions:
            raise '--subscribe and --fsubscribe keys can not be used together'
        chain = (bot.subscribe, )
        allowed_actions.append((bot.condition, chain, (bot.filter, ))
    elif action == '--story':
        allowed_actions.append((bot.see_stories,))


    
