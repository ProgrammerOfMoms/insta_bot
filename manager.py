from bot import *

class BotManager():
    def __init__(self, login, password, allowed_actions=[]):
        self.bot = Bot(login, password)
        self.allowed_actions = allowed_actions

    def auth(self):
        self.bot.auth()
        return self

    def go_to_tags_page(self, tag):
        wait = WebDriverWait(self.bot.browser, 5)
        try:
            input_f = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="react-root"]/section/nav/div[2]/div/div/div[2]/div')))
        except:
            self.bot.get("https://www.instagram.com")
            input_f = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="react-root"]/section/nav/div[2]/div/div/div[2]/div')))
        ActionChains(self.bot.browser).move_to_element(input_f).click().send_keys(tag).pause(1).send_keys(Keys.ENTER).pause(1).send_keys(Keys.ENTER).perform()
        return self
    
    def parse_tags_page(self, count):
        wait = WebDriverWait(self.bot.browser, 5)
        scrollWait = WebDriverWait(self.bot.browser, 10)
        if 'like' in self.allowed_actions and 'subscribe' in self.allowed_actions:
            actions = [[self.bot.like, ], [self.bot.subscribe], [self.bot.wait, 'subscribe']]
            photo_class = '_9AhH0'
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, photo_class)))
            self.bot.wait()
            objs = self.bot.browser.find_elements_by_class_name(photo_class)
            i = 0
            while i < count:
                for obj in objs:
                    print(obj)
                    ActionChains(self.bot.browser).move_to_element(obj).click().perform()
                    title = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[4]/div[2]/div/article/header/div[2]/div[1]/div[1]/h2/a")))
                    title = title.get_attribute('title')
                    target = "https://www.instagram.com/"+title
                    cond = [(self.bot.filter, target)]
                    # self.bot.condition(actions, cond)
                    time.sleep(0.5)
                    self.bot.browser.back()
                    if i > count:
                        return self
                    i += 1
                # print('now scroll')
                # time.sleep(2)
                # last_num = len(objs)-1
                # last_obj = objs[last_num]
                # ActionChains(self.bot.browser).key_down(Keys.DOWN).perform()
                # scrollWait.until(EC.invisibility_of_element_located(last_obj))
                # ActionChains(self.bot.browser).key_up(Keys.DOWN).perform()
                objs = self.bot.browser.find_elements_by_class_name(photo_class)
                print(i)
            return self
        else:
            return self

