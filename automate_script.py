from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from lxml import html
from selenium.webdriver.chrome.options import Options
import re

chrome_options = Options()
chrome_options.add_argument("--kiosk")

def gap_half():
    time.sleep(.5)

def gap_1s():
    time.sleep(1)

def gap_2s():
    time.sleep(2)

class SendRequests:
    button_click_xpath = '(//div[@class="search-result__wrapper"])[{}]//button'
    next_button_xpath = '//span[text()="Next" and @class="artdeco-button__text"]'
    dialog_exist_xpath = '//div[@class="ph4"]/label[@for="email"]'

    def __init__(self, note_text):
        self.base_url = 'https://www.linkedin.com'
        self.browser = webdriver.Chrome('webdriver/chromedriver',chrome_options=chrome_options)
        self.note_text = note_text

    def login(self):
        self.browser.get(self.base_url)
        username, password = self.get_email_pass()
        self.browser.get(self.base_url + '/uas/login')
        emailElement = self.browser.find_element_by_id('username')
        emailElement.send_keys(username)
        passElement = self.browser.find_element_by_id('password')
        passElement.send_keys(password)
        passElement.submit()
        print('Signing in...')
        gap_2s()

    def search(self, query):
        search_bar_element = self.browser.find_element_by_xpath('//input[@placeholder="Search"]')
        search_bar_element.send_keys(query)
        search_bar_element.send_keys(Keys.ENTER)
        gap_2s()

    def switch_to_people(self):
        people_button = self.browser.find_element_by_xpath('//span[text()="People"]')
        people_button.click()
        gap_2s()

    def get_names_button_texts_links(self):
        html_page = html.fromstring(self.browser.page_source)
        profile_link_xpath = '//div[@class="search-result__info pt3 pb4 ph0"]'
        profile_link_elements = html_page.xpath(profile_link_xpath)
        profile_links = [self.base_url + el.xpath('./a/@href')[0] for el in profile_link_elements]
        name_texts = [el.xpath('.//span[@class="name actor-name"]/text()')[0] for el in profile_link_elements]

        button_text_xpath = '(//div[@data-control-name="srp_profile_actions"]/button)|(//div[@class="search-result__actions"]/div/button)'
        button_elements = html_page.xpath(button_text_xpath)
        button_texts = [el.attrib['aria-label'] for el in button_elements]

        return profile_links, name_texts, button_texts

    def send_requests(self):
        for i in range(1, 100):

            pl, nt, bt = self.get_names_button_texts_links()

            for i, tup in enumerate(zip(pl, nt, bt)):
                if html.fromstring(self.browser.page_source).xpath(self.dialog_exist_xpath):
                    self.browser.find_element_by_xpath('//button[@name="cancel"]').click()
                    time.sleep(0.7)
                self.adjust_window(i)

                link, name, button_text = tup

                if button_text.startswith('Invite Sent'):
                    continue

                elif button_text.startswith('Connect'):
                    button_click_element = self.browser.find_element_by_xpath(self.button_click_xpath.format(i + 1))
                    button_click_element.click()
                    self.add_note_and_send(name)
                    time.sleep(1)

                elif button_text.startswith('Follow') or button_text.startswith('Message') or button_text.startswith('Send'):
                    self.browser.execute_script('''window.open("","_blank");''')
                    tabs = self.browser.window_handles
                    self.browser.switch_to.window(tabs[1])
                    self.browser.get(link)
                    time.sleep(1)
                    # close chat box
                    self.browser.find_element_by_xpath('//span[text()="Messaging" and @aria-hidden="true"]').click()
                    time.sleep(1)
                    # get_connect_button
                    try:
                        connect_button = self.find_connect_button()
                        connect_button.click()
                        self.add_note_and_send(name)
                    except:
                        print('The connect button does not exist on the page.')
                    self.browser.close()
                    self.browser.switch_to.window(tabs[0])
                    time.sleep(0.5)
            time.sleep(1)
            self.next_page()

    def next_page(self, skip_to=None):
        if html.fromstring(self.browser.page_source).xpath(self.dialog_exist_xpath):
            self.browser.find_element_by_xpath('//button[@name="cancel"]').click()
            time.sleep(0.7)
        if skip_to:
            current_url = self.browser.current_url
            modified_url = re.sub('&page=\d+', '', current_url)
            modified_url = modified_url + '&page={}'.format(skip_to)
            self.browser.get(modified_url)
        self.page_down()
        self.browser.find_element_by_xpath(self.next_button_xpath).click()
        time.sleep(4)

    def add_note_and_send(self, name):
        name = SendRequests.text_decode(name)
        name = name.split()[0]
        text = f'Hello {name},\n{self.note_text}'
        add_note_button_xpath = '//button[@class="artdeco-button artdeco-button--secondary artdeco-button--3 mr1"]'
        add_text_xpath = '//textarea[@class="send-invite__custom-message mb3 ember-text-area ember-view"]'
        invite_send_button_xpath = '//button[text()="Send invitation"]'
        add_button_element = self.browser.find_element_by_xpath(add_note_button_xpath)
        add_button_element.click()
        text_area_element = self.browser.find_element_by_xpath(add_text_xpath)
        text_area_element.send_keys(text)
        invite_send_button_element = self.browser.find_element_by_xpath(invite_send_button_xpath)
        invite_send_button_element.click()
        time.sleep(1)

    def find_connect_button(self):
        html_page = html.fromstring(self.browser.page_source)
        connect_button_on_profile_xpath = '//span[@class="artdeco-button__text" and text()="Connect"]'
        more_button_xpath = '//span[@class="artdeco-button__text" and text()="More…"]'
        more_button_connect_xpath = '//span[@class="display-flex t-normal pv-s-profile-actions__label" and text()="Connect"]'
        if html_page.xpath(connect_button_on_profile_xpath):
            connect_element = self.browser.find_element_by_xpath(connect_button_on_profile_xpath)
            return connect_element
        else:
            more_element = self.browser.find_element_by_xpath(more_button_xpath)
            more_element.click()
            time.sleep(1)
            connect_element = self.browser.find_element_by_xpath(more_button_connect_xpath)
            return connect_element

    def page_down(self):
        self.browser.find_element_by_xpath('//body').send_keys(Keys.PAGE_DOWN)
        time.sleep(1)

    def page_up(self):
        self.browser.find_element_by_xpath('//body').send_keys(Keys.PAGE_UP)
        time.sleep(1)

    def adjust_window(self, index):
        self.browser.execute_script('''window.scrollTo(0,{});'''.format(110*index))
        time.sleep(0.5)

    @staticmethod
    def text_decode(text):
        return text.encode('ascii', 'replace').decode().replace('?', '').strip()

    def get_email_pass(self):
        try:
            with open('config', 'r') as f:
                username, password = f.read().split('\n')
            return username, password
        except:
            print("The format you specified in config file is wrong. Use prompt to provide username and password.")
            username = input('Enter linked in user email id')
            password = input('Enter the password.')
            if self.is_email_valid(email=username):
                return username, password

    def is_email_valid(self, email):
        return True