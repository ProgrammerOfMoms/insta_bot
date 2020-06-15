from bot import Bot

bot = Bot('programmer_of_mom', 'qawsedrf123')
# bot.auth().get("https://www.instagram.com/p/B7tARVwogs3/").see_stories().test().quit()

actions = [(bot.like, )]

bot.auth().get(bot.my_page).wait().map(actions, '_9AhH0').wait().quit()