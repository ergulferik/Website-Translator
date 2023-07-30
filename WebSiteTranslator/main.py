import os
import time
import threading
import scrapy
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import pyautogui
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


class LinkSaver:
    def __init__(self, mainPage, TXT_NAME="Links"):
        chromedriver_autoinstaller.install()
        service = Service("C:/Users/erg_m/PycharmProjects/WebSiteTranslator/chromedriver.exe")
        self._driver = webdriver.Chrome(service=service)
        self._mainPage = mainPage
        self._TXT_NAME = TXT_NAME

        with open(self._TXT_NAME + ".txt", "w"):
            pass

    def SaveOneLevelLinks(self):
        currentLink = self._mainPage
        self._driver.get(currentLink)
        links = self._driver.find_elements(By.XPATH, '//a')
        for link in links:
            self._SaveLinks(str(link.get_attribute("href")))

    def _SaveLinks(self, link):
        with open(self._TXT_NAME + ".txt", "r") as read:
            flag = False
            for linkInTXT in read.readlines():
                if linkInTXT.strip() == link:
                    flag = True

        if not flag and link.startswith(self._mainPage):
            with open(self._TXT_NAME + ".txt", "a") as append:
                append.write(link + "\n")


class WebSiteTranslator:

    def __init__(self, MAIN_PAGE, LANG='en', TXT_NAME="Links"):
        self._driver = None
        self._actions = None
        chromedriver_autoinstaller.install()
        self._TXT_NAME = TXT_NAME
        self._LANG = LANG
        self._mainPage = MAIN_PAGE
        self.savedLinks = []
        service = Service("C:/Users/erg_m/PycharmProjects/WebSiteTranslator/chromedriver.exe")
        options = webdriver.ChromeOptions()
        options.add_argument('--lang=' + self._LANG)
        prefs = {
            "translate": {"enabled": "true"}
        }
        options.add_experimental_option("prefs", prefs)
        options.page_load_strategy = 'normal'
        self._options = options
        self._service = service
        self._linkCount = 0
        with open(self._TXT_NAME + ".txt", 'r') as f:
            for _ in f:
                self._linkCount += 1

    def _ModifyUrls(self, html):
        soup = BeautifulSoup(html, 'html.parser', from_encoding="utf-8")
        f = open("links.txt", 'r')
        allLinks = f.read()
        for a_tag in soup.find_all('a'):
            if str(a_tag['href']).strip() in allLinks or self._mainPage[:-1] + str(a_tag['href']).strip() in allLinks:
                a_tag['href'] = self._CreateFileName(a_tag['href'])

        return soup.prettify()

    def _CreateFileName(self, url):
        url = url.strip()
        if len(url) <= 1:
            return "index.html"
        if url == self._mainPage or url == self._mainPage[:-1]:
            return "index.html"
        if url.endswith("/"):
            url = url[:-1]
        if url.startswith(self._mainPage):
            url = url.strip().replace(self._mainPage, "").replace("/", "-")
        elif url.startswith("/"):
            url = url[1:].replace("/", "-")
        return url + ".html"

    def Translate(self):
        if self._AreYouSure():
            currentLinkCount = 0
            self._driver = webdriver.Chrome(options=self._options, service=self._service)
            self._actions = ActionChains(self._driver)
            self._driver.maximize_window()
            with open(self._TXT_NAME + ".txt") as in_file:
                for url in in_file:
                    # region Opening URL
                    self._driver.switch_to.new_window('tab')
                    url = url.strip()
                    self._driver.get(url)
                    wait = WebDriverWait(self._driver, 10)
                    wait.until(ec.presence_of_element_located((By.XPATH, "//body")))
                    # endregion

                    # region Choosing Google Translate
                    if self._driver.execute_script("return document.documentElement.lang") != self._LANG:
                        self._actions.move_by_offset(0, 0).context_click().perform()
                        time.sleep(0.2)
                        for i in range(8):
                            pyautogui.press('down')
                            time.sleep(0.1)
                        pyautogui.press('enter')
                        time.sleep(2)
                    # endregion

                    # region Move Down
                    screen_height = self._driver.execute_script("return window.screen.height;")
                    i = 1
                    while True:
                        self._driver.execute_script(
                            "window.scrollTo(0, {screen_height}*{i});".format(screen_height=screen_height, i=i / 2))
                        i += 1
                        time.sleep(0.2)
                        if (screen_height) * i / 2 > self._driver.execute_script(
                                "return document.body.scrollHeight;"):
                            break
                    # endregion

                    # region Saving
                    file1 = open(self._CreateFileName(url), 'w', encoding="utf-8")
                    file1.write(self._ModifyUrls(self._driver.page_source))
                    file1.close()
                    # endregion

                    currentLinkCount += 1
                    print(str(currentLinkCount) + "/" + str(self._linkCount))

    def _AreYouSure(self):

        userInput = input(
            f"You have {self._linkCount} links, do you want to translate all of them? [Y]es or [N]o\n").capitalize()
        return userInput == 'Y' or userInput == 'YES'


ls = LinkSaver("https://www.classcentral.com/", "links")
ls.SaveOneLevelLinks()
wst = WebSiteTranslator("https://www.classcentral.com/", "hi", "links")
wst.Translate()
