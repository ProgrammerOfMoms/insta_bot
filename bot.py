# -*- coding: utf-8 -*-

import settings
import utils
import os
import pickle
import time
import random

from db import DataBase

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException

from nltk.tokenize import TweetTokenizer

class Bot():

    def __init__(self, login, password):
        self.login = login
        self.password = password
        self.cookies = settings.COOKIES_DIR+login+'_'+settings.COOKIES_FILENAME_BASE
        self.db = DataBase()
        self.browser = webdriver.Chrome(settings.DRIVER_PATH)
        self.browser.implicitly_wait(3)
        self.db.init_tables()
        self.my_page = "https://www.instagram.com/"+login
        self._filter_model = None
        self._count_vec = None
        self._tf_transformer = None


    def _load_ml_model(self):
        if self._filter_model == None:
            with open(settings.FILTER_MODEL_PATH, 'rb') as f:
                self._filter_model = pickle.load(f)
        if self._count_vec == None:
            with open(settings.COUNT_VEC_PATH, 'rb') as f:
                self._count_vec = pickle.load(f)
        if self._tf_transformer == None:
            with open(settings.TF_VEC_PATH, 'rb') as f:
                self._tf_transformer = pickle.load(f)
    
    def _load_cookies(self):
        """cookies loader"""
        if not os.path.exists(self.cookies):
            return False
        
        cookies = pickle.load(open(self.cookies, "rb"))
        for cookie in cookies:
            if 'expiry' in cookie:
                del cookie['expiry']
            self.browser.add_cookie(cookie)
        return True

    def _save_cookies(self):
        """cookies saver"""
        pickle.dump(self.browser.get_cookies() , open(self.cookies,"wb"))
    
    def wait(self, action = None):
        if action == 'like':
            time.sleep(random.uniform(15, 40))
            return self
        elif action == 'subscribe':
            time.sleep(random.uniform(15, 40))
            return self
        elif action == 'unsubscribe':
            time.sleep(random.uniform(40, 60))
            return self
        else:
            time.sleep(random.uniform(3, 5))
            return self


    def get(self, url):
        self.browser.get(url)
        return self
    
    def auth(self):
        wait = WebDriverWait(self.browser, 5)
        self.browser.get('https://www.instagram.com/accounts/login/?source=auth_switcher')
        self._load_cookies()
        self.browser.refresh()
        if self.browser.current_url == "https://www.instagram.com/":
            self._save_cookies()
            self.db.update_user(self.login)
            try:
                wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[4]/div/div')))
                not_now_btn = self.browser.find_element_by_xpath('/html/body/div[4]/div/div/div[3]/button[2]')
                ActionChains(self.browser).move_to_element(not_now_btn).click().perform()
            except TimeoutException:
                pass
            return self
        else:
            wait = WebDriverWait(self.browser, 5)
            login_field = wait.until(
                EC.presence_of_element_located((By.XPATH, "//section/main/div/article/div/div[1]/div/form/div[2]/div/label/input")))
            password_field = wait.until(
                EC.presence_of_element_located((By.XPATH, "//section/main/div/article/div/div[1]/div/form/div[3]/div/label/input")))
            login_btn = wait.until(
                EC.presence_of_element_located((By.XPATH, "//section/main/div/article/div/div[1]/div/form/div[4]")))
            ActionChains(self.browser).move_to_element(login_field).click().send_keys(self.login).move_to_element(password_field).click().send_keys(self.password).move_to_element(login_btn).click().perform()
            
            wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, 'piCib')))
            
            print(self.browser.current_url)
            if self.browser.current_url == "https://www.instagram.com/":
                self._save_cookies()
                if not self.db.add_new_user(self.login):
                    self.db.update_user(self.login)
                try:
                    wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[4]/div/div')))
                    not_now_btn = self.browser.find_element_by_xpath('/html/body/div[4]/div/div/div[3]/button[2]')
                    ActionChains(self.browser).move_to_element(not_now_btn).click().perform()
                except TimeoutException:
                    pass
                return self
            else:
                self.db.add_action(self.login, 'auth_error', self.browser.current_url)
                return False
    
    def like(self):
        try:
            like_btn = self.browser.find_element_by_class_name('wpO6b')
            text = like_btn.find_element_by_tag_name('svg').get_attribute('aria-label')
            if text.lower() == 'нравится':
                ActionChains(self.browser).move_to_element(like_btn).click().perform()
                self.db.add_action(self.login, 'like', self.browser.current_url)
                return self
            else:
                return self
        except NoSuchElementException as e:
            self.db.add_action(self.login, 'like_error', str(e))
            return False
        except Exception as e:
            self.db.add_action(self.login, 'like_error', str(e))
            return False

    def subscribe(self):
        try:
            wait = WebDriverWait(self.browser,  5)
            sub_btn = self.browser.find_element_by_xpath('//button[text()="Подписаться"]')
            ActionChains(self.browser).move_to_element(sub_btn).click().perform()
            try:
                title = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/section/main/div/div/article/header/div[2]/div[1]/div[1]/h2/a")))
                title = title.get_attribute('title')
                print(title)
                self.db.add_action(self.login, 'subscribe', "https://www.instagram.com/"+title)
                return self
            except TimeoutException:
                self.db.add_action(self.login, 'subscribe', self.browser.current_url)
                return self 
        except NoSuchElementException:
            self.db.add_action(self.login, 'subscribe_error', self.browser.current_url)
            return False


    def unsubscribe(self):
        try:
            wait = WebDriverWait(self.browser,  5)
            sub_btn = self.browser.find_element_by_xpath('//button[text()="Подписки"]')
            ActionChains(self.browser).move_to_element(sub_btn).click().perform()
            confirm_btn = wait.until(EC.presence_of_element_located((By.XPATH, '//button[text()="Отменить подписку"]')))
            ActionChains(self.browser).move_to_element(confirm_btn).click().perform()
            try:
                title = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/section/main/div/div/article/header/div[2]/div[1]/div[1]/h2/a")))
                title = title.get_attribute('title')
                self.db.add_action(self.login, 'unsubscribe', "https://www.instagram.com/"+title)
                return self
            except TimeoutException:
                self.db.add_action(self.login, 'unsubscribe', self.browser.current_url)
                return self 
        except:
            self.db.add_action(self.login, 'unsubscribe_error', self.browser.current_url)
            return False


#/html/body/div[1]/section/div/div/section/div[2]/div[1]/div/div/div[2]/div/div[1]
#B20bj
    def see_stories(self):
        wait = WebDriverWait(self.browser, 5)
        waitStory = WebDriverWait(self.browser, 120)
        try:
            try:
                story_btn = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/section/main/div/div/article/header/div[1]/span")))
                ActionChains(self.browser).move_to_element(story_btn).click().perform()
                try:
                    waitStory.until(EC.invisibility_of_element_located((By.XPATH, '//*[@id="react-root"]/section/div/div')))
                except TimeoutException:
                    exit_btn = self.browser.find_element_by_xpath('//*[@id="react-root"]/section/div/div/section/div[2]/button[3]/div/span')
                    ActionChains(self.browser).move_to_element(exit_btn).click().perform()
                finally:
                    title = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/section/main/div/div/article/header/div[2]/div[1]/div[1]/h2/a")))
                    title = title.get_attribute('title')
                    self.db.add_action(self.login, 'story', "https://www.instagram.com/"+title)
                    return self
            except TimeoutException:
                account_btn = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="react-root"]/section/main/div/div/article/header/div[1]')))      
                ActionChains(self.browser).move_to_element(account_btn).click().perform()
                story_btn = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="react-root"]/section/main/div/header/div/div')))
                ActionChains(self.browser).move_to_element(story_btn).click().perform()
                try:
                    story_win = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="react-root"]/section/div/div')))
                except TimeoutException:
                    self.db.add_action(self.login, 'no_story', self.browser.current_url)
                    return self
                try:
                    waitStory.until(EC.invisibility_of_element_located((By.XPATH, '//*[@id="react-root"]/section/div/div')))
                except TimeoutException:
                    exit_btn = self.browser.find_element_by_xpath('//*[@id="react-root"]/section/div/div/section/div[2]/button[3]/div/span')
                    ActionChains(self.browser).move_to_element(exit_btn).click().perform()
                finally:
                    self.db.add_action(self.login, 'story', self.browser.current_url)
                    return self
        except TimeoutException:
            story_btn = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="react-root"]/section/main/div/header/div/div')))
            ActionChains(self.browser).move_to_element(story_btn).click().perform()
            try:
                story_win = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="react-root"]/section/div/div')))
            except TimeoutException:
                self.db.add_action(self.login, 'no_story', self.browser.current_url)
                return self
            try:
                waitStory.until(EC.invisibility_of_element_located((By.XPATH, '//*[@id="react-root"]/section/div/div')))
            except TimeoutException:
                exit_btn = self.browser.find_element_by_xpath('//*[@id="react-root"]/section/div/div/section/div[2]/button[3]/div/span')
                ActionChains(self.browser).move_to_element(exit_btn).click().perform()
            finally:
                self.db.add_action(self.login, 'story', self.browser.current_url)
                return self
    
    def _filter_model_worker(self, desc):
        tokenizer = TweetTokenizer()
        preprocess = lambda text: ' '.join(tokenizer.tokenize(text.lower()))
        desc = [desc]
        sent = [preprocess(x) for x in desc]
        print(sent)
        sent = self._count_vec.transform(sent)
        sent_tfidf = self._tf_transformer.transform(sent)
        predict = self._filter_model.predict_proba(sent_tfidf)
        print("model: {}".format(predict[0]))
        if predict[0][1] >= 0.7:
            return True
        return False

    def filter(self, account_url):
        self._load_ml_model()
        self.browser.get(account_url)
        wait = WebDriverWait(self.browser, 5)
        desc_block = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="react-root"]/section/main/div/header/section/div[2]')))
        desc = desc_block.text
        self.browser.back()
        if self._filter_model_worker(desc):
            return True
        else:
            return False

    def open_first_photo(self):
        wait = WebDriverWait(self.browser, 5)
        try:
            photo = wait.until(EC.presence_of_element_located((By.CLASS_NAME, '_9AhH0')))
        except:
            return False
        ActionChains(self.browser).move_to_element(photo).click().perform()
        return self


    def _call_action(self, action):
        s = len(action)
        func = action[0]
        args = []
        for i in range(1, s):
            args.append(action[i])
        return func(*args)
    
    def condition(self, action_chain, cond):
        if self._call_action(cond):
            for action in action_chain:
                self._call_action(action)
            return self
        else:
            return self
    
    def map(self, action_chain, objects, cond=None, count = None):
        if cond == None:
            cond = (lambda: True, )
        try:
            i = 0
            for obj in objects:
                obj.click()
                self.condition(action_chain, cond)
                self.browser.back()
                if count != None and i > count:
                    return self
                i += 1
            return self
        except TimeoutException:
            return False


    
    def quit(self):
        self._save_cookies()
        self.browser.quit()


    # def test(self):
    #     sql = """select * from History"""
    #     self.db.execute_sql(sql)
    #     d = self.db.cursor.fetchall()
    #     print(d)
    #     sql = 'delete from History'
    #     self.db.execute_sql(sql)
    #     return self

