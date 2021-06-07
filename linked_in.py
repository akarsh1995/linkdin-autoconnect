from browser import BaseAction
from selenium import webdriver
from time import sleep
from selenium.webdriver.common.keys import Keys
from random import choice

from random import randint

def random_gaps0_5():
    sleep(randint(0, 5))

class Login(BaseAction):
    browser = webdriver.Chrome
    base_url = 'https://linkedin.com'
    remmber_me_button = '//button[text()="Remember"]'
    logged_in_hook = '//span[text()="Start a post"]'

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def is_logged_in(self):
        return self.wait_and_check_presence(self.logged_in_hook)

    def login(self):
        self.browser.get(url=self.base_url + '/login')
        self.wait_and_send_keys('//input[@id="username"]', self.username)
        self.wait_and_send_keys('//input[@id="password"]', self.password)
        self.wait_and_click('//button[@type="submit"]')
        print('Signing in...')
        random_gaps0_5()
        self.wait_and_click(self.remmber_me_button)

    def action(self):
        if self.is_logged_in():
            return
        else:
            self.login()


class Search(BaseAction):
    search_bar_xpath = '//input[@placeholder="Search"]'
    xpath_see_all_people = '(//*[text()="See all people results"])[1]'

    def __init__(self, query):
        self.query = query

    def action(self):
        if self.search_bar_exists:
            self.wait_and_send_keys(self.search_bar_xpath, self.query)
            self.wait_and_send_keys(self.search_bar_xpath, Keys.ENTER)
            self.wait_and_click(self.xpath_see_all_people)
            sleep(2)

    @property
    def search_bar_exists(self):
        return True

class ConnectionDialogHandler(BaseAction):
    xpath_add_note = '//span[text()="Add a note"]'
    xpath_message_text_box = '//textarea'
    xpath_send_button = '//span[text()="Send"]'

    def __init__(self, text_notes):
        self._text_notes = text_notes

    def action(self):
        self.wait_and_click(self.xpath_add_note)
        random_gaps0_5()
        self.wait_and_send_keys(self.xpath_message_text_box, self._text_note)
        random_gaps0_5()
        self.wait_and_click(self.xpath_send_button)

    @property
    def text_note(self):
        return choice(self._text_notes)

    def __call__(self, browser, name):
        name = name.encode('ascii', 'replace').decode().replace('?', '').strip()
        self._text_note = self.text_note.format(name)
        return super().__call__(browser)


class SendRequest(BaseAction):

    def __init__(self, connection_dialogue_handler: ConnectionDialogHandler):
        self.connection_dialogue_handler = connection_dialogue_handler

    def __call__(self, browser, name, link,  button, element_id):
        self.link = link
        self.name = name
        self._button = button
        self.element_id = element_id
        super().__call__(browser)

    def action(self):
        self.adjust_window(self.element_id)
        if self.connect_button_found:
            self.button.click()
            self.connection_dialogue_handler(self.browser, self.name)

    @property
    def button(self):
        if self.connect_button_found:
            return self._button['connect']
        elif self.follow_button_found:
            return self._button['follow']
        elif self.message_button_found:
            return self._button['message']

    @property
    def connect_button_found(self):
        return 'connect' in self._button

    @property
    def follow_button_found(self):
        return 'follow' in self._button

    @property
    def message_button_found(self):
        return 'message' in self._button


class ConnectionsIterator(BaseAction):
    xpath_profile_image = '(//img[@width="48"]|//div[@class="visually-hidden"])'
    xpath_next_button = '//span[text()="Next"]'

    def __init__(self, browser):
        self.browser = browser

    def __iter__(self):
        while True:
            if self.wait_and_check_presence(self.xpath_profile_image):
                profile_pic_elems = self.browser.find_elements_by_xpath(self.xpath_profile_image)
                sleep(2)
                for index, profile_pic_elem in enumerate(profile_pic_elems):
                    if profile_pic_elem.tag_name == 'div':
                        connection_name = profile_pic_elem.text
                    else:
                        connection_name = profile_pic_elem.get_attribute('alt')
                    connection_link = profile_pic_elem.find_element_by_xpath(
                        'ancestor::a'
                    ).get_attribute('href')
                    button = profile_pic_elem.find_element_by_xpath(
                        'ancestor::li//span[text()="Connect" or text()="Follow" or text()="Message" or text()="Pending"]'
                    )
                    button_present = {
                        button.text.lower(): button
                    }
                    yield connection_name, connection_link, button_present, index
                self.adjust_window(12)
                self.wait_and_click(self.xpath_next_button)
            else:
                raise TypeError('Tried to find profile picture elements but element not found.')
