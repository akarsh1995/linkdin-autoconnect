from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from lxml import html
from selenium.webdriver.chrome.options import Options
import re
from xpaths import NavigationXpaths as nx
import os

chrome_options = Options()
chrome_options.add_argument("--kiosk")

def gap_half():
    time.sleep(.5)

def gap_1s():
    time.sleep(1)

def gap_2s():
    time.sleep(2)

class SendRequests:


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
        search_bar_element = self.browser.find_element_by_xpath(nx.search_bar_xpath)
        search_bar_element.send_keys(query)
        search_bar_element.send_keys(Keys.ENTER)
        gap_2s()

    def switch_to_people(self):
        people_button = self.browser.find_element_by_xpath(nx.people_button_xpath)
        people_button.click()
        gap_2s()

    def get_names_button_texts_links(self):
        html_page = html.fromstring(self.browser.page_source)
        profile_link_elements = html_page.xpath(nx.profile_link_xpath)
        profile_links = [self.base_url + el.xpath('./a/@href')[0] for el in profile_link_elements]
        name_texts = [el.xpath('.//span[@class="name actor-name"]/text()')[0] for el in profile_link_elements]

        button_elements = html_page.xpath(nx.button_text_xpath)
        button_texts = [el.attrib['aria-label'] if 'aria-label' in el.keys() else '' for el in button_elements]

        return profile_links, name_texts, button_texts

    def send_requests(self):
        for i in range(1, 100):

            pl, nt, bt = self.get_names_button_texts_links()

            for i, tup in enumerate(zip(pl, nt, bt)):
                self.adjust_window(i)

                link, name, button_text = tup

                if button_text.startswith('Invite Sent'):
                    continue

                elif button_text.startswith('Connect'):
                    button_click_element = self.browser.find_element_by_xpath(nx.button_click_xpath.format(i + 1))
                    button_click_element.click()
                    self.add_note_and_send(name)
                    time.sleep(1)

                else:
                    self.browser.execute_script('''window.open("","_blank");''')
                    tabs = self.browser.window_handles
                    self.browser.switch_to.window(tabs[1])
                    self.browser.get(link)
                    time.sleep(1)
                    # close chat box
                    self.browser.find_element_by_xpath(nx.message_chat_bar_xpath).click()
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

        self.page_down()
        self.browser.find_element_by_xpath(nx.next_button_xpath).click()
        time.sleep(4)

    def jump_to(self, page_no):
        current_url = self.browser.current_url
        modified_url = re.sub('&page=\d+', '', current_url)
        modified_url = modified_url + '&page={}'.format(page_no)
        self.browser.get(modified_url)

    def add_note_and_send(self, name):
        name = SendRequests.text_decode(name)
        name = name.split()[0]
        text = f'Hello {name},\n{self.note_text}'

        add_button_element = self.browser.find_element_by_xpath(nx.add_note_button_xpath)
        add_button_element.click()
        text_area_element = self.browser.find_element_by_xpath(nx.add_text_xpath)
        text_area_element.send_keys(text)
        invite_send_button_element = self.browser.find_element_by_xpath(nx.invite_send_button_xpath)
        try:
            invite_send_button_element.click()
        except:
            if html.fromstring(self.browser.page_source).xpath(nx.dialog_exist_xpath):
                self.browser.find_element_by_xpath(nx.cancel_button_xpath).click()
                time.sleep(0.7)
        time.sleep(1)

    def find_connect_button(self):
        html_page = html.fromstring(self.browser.page_source)

        if html_page.xpath(nx.connect_button_on_profile_xpath):
            connect_element = self.browser.find_element_by_xpath(nx.connect_button_on_profile_xpath)
            return connect_element
        else:
            more_element = self.browser.find_element_by_xpath(nx.more_button_xpath)
            more_element.click()
            time.sleep(1)
            connect_element = self.browser.find_element_by_xpath(nx.more_button_connect_xpath)
            return connect_element

    def page_down(self):
        self.browser.find_element_by_xpath(nx.body_xpath).send_keys(Keys.PAGE_DOWN)
        time.sleep(1)

    def page_up(self):
        self.browser.find_element_by_xpath(nx.body_xpath).send_keys(Keys.PAGE_UP)
        time.sleep(1)

    def adjust_window(self, index):
        self.browser.execute_script('''window.scrollTo(0,{});'''.format(110*index))
        time.sleep(0.5)

    @staticmethod
    def text_decode(text):
        return text.encode('ascii', 'replace').decode().replace('?', '').strip()

    def get_email_pass(self):
        try:
            username = os.environ.get('LINKEDIN_USER')
            password = os.environ.get('LINKEDIN_PASS')
            return username, password
        except:
            print("The env vars does not seem to be set please use the console.")
            username = input('Enter linked in user email id')
            password = input('Enter the password.')
            if self.is_email_valid(email=username):
                return username, password

    def is_email_valid(self, email):
        return True