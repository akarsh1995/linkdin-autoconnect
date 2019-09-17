import os
import re
import time

from lxml import html
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

from xpaths import NavigationXpaths as nx

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
        self.browser = webdriver.Chrome('webdriver/chromedriver', chrome_options=chrome_options)
        self.note_text = note_text

    def login(self):
        self.browser.get(self.base_url)
        username, password = self.get_email_pass()
        self.browser.get(self.base_url + '/uas/login')
        self.send_keys(username, '//input[@id="username"]')
        self.send_keys(password, '//input[@id="password"]')
        self.click('//button[@type="submit"]')
        print('Signing in...')
        gap_2s()

    def search(self, query):
        self.send_keys(query, nx.search_bar_xpath)
        self.send_keys(Keys.ENTER, nx.search_bar_xpath)
        gap_2s()

    def switch_to_people(self):
        self.click(nx.people_button_xpath)
        gap_2s()

    def get_names_button_texts_links(self):
        self.page_down()
        self.page_down()
        gap_1s()
        # get names
        profile_link_elements = self.xpath_from_string(nx.profile_link_xpath)
        profile_links = [self.base_url + el.xpath('./a/@href')[0] for el in profile_link_elements]
        name_texts = [el.xpath('.//span[@class="name actor-name"]/text()')[0] for el in profile_link_elements]

        # get button texts
        button_elements = self.xpath_from_string(nx.button_text_xpath)
        button_texts = [el.attrib['aria-label'] if 'aria-label' in el.keys() else '' for el in button_elements]
        self.page_up()
        self.page_up()
        return profile_links, name_texts, button_texts

    def send_requests(self):
        try:
            for i in range(1, 100):

                pl, nt, bt = self.get_names_button_texts_links()

                for i, (link, name, button_text) in enumerate(zip(pl, nt, bt)):
                    self.adjust_window(i)

                    if button_text.startswith('Invite sent'):
                        continue

                    elif button_text.startswith('Connect'):
                        try:
                            self.click(nx.button_click_xpath.format(i + 1))
                            self.add_note_and_send(name)
                            time.sleep(1)
                        except:
                            continue

                    else:
                        self.open_new_tab()
                        self.browser.get(link)
                        gap_2s()
                        try:
                            self.click_connect_button()
                            self.add_note_and_send(name)
                            self.close_and_switch_tab()
                        except:
                            self.close_and_switch_tab()
                            print('The connect button does not exist on the page.')
                time.sleep(1)
                self.write_page()
                self.next_page()
        except RuntimeError:
            print("there's an error")
        finally:
            self.close_browser()

    def next_page(self, skip_to=None):
        self.page_down()
        self.click(nx.next_button_xpath)
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

        self.click(nx.add_note_button_xpath)
        self.send_keys(text, nx.add_text_xpath)
        self.click(nx.invite_send_button_xpath)
        self.close_dialog_box()
        time.sleep(1)

    def click_connect_button(self):

        if self.xpath_from_string(nx.connect_button_on_profile_xpath):
            self.find(nx.connect_button_on_profile_xpath).click()
        else:
            self.click(nx.more_button_xpath)
            time.sleep(0.5)
            self.find(nx.more_button_connect_xpath).click()

    def close_dialog_box(self):
        if self.xpath_from_string(nx.cancel_button_xpath):
            self.click(nx.cancel_button_xpath)
            time.sleep(0.7)

    def page_down(self):
        self.send_keys(Keys.PAGE_DOWN, nx.body_xpath)
        time.sleep(0.5)

    def page_up(self):
        self.send_keys(Keys.PAGE_UP, nx.body_xpath)
        time.sleep(0.5)

    def adjust_window(self, index):
        self.browser.execute_script('''window.scrollTo(0,{});'''.format(110 * index))
        time.sleep(0.5)

    @staticmethod
    def text_decode(text):
        return text.encode('ascii', 'replace').decode().replace('?', '').strip()

    def click(self, xpath):
        self.find(xpath).click()

    def send_keys(self, keys, xpath):
        self.find(xpath).send_keys(keys)

    def find(self, xpath):
        return self.browser.find_element_by_xpath(xpath)

    def xpath_from_string(self, xpath):
        html_page = html.fromstring(self.browser.page_source)
        return html_page.xpath(xpath)

    def open_new_tab(self):
        self.browser.execute_script('''window.open("","_blank");''')
        self.tabs = self.browser.window_handles
        self.browser.switch_to.window(self.tabs[1])

    def close_and_switch_tab(self):
        self.browser.close()
        self.browser.switch_to.window(self.tabs[0])
        time.sleep(0.5)

    def close_browser(self):
        self.browser.close()

    def get_email_pass(self):
        try:
            username = os.environ.get('LINKEDIN_USER')
            password = os.environ.get('LINKEDIN_PASS')
            return username, password
        except:
            print("The env vars does not seem to be set please use the console.")
            username = input('Enter linked in user email id')
            password = input('Enter the password.')
            return username, password

    def get_current_page_number(self):
        return self.xpath_from_string(nx.current_page_number_text)[0]

    def write_page(self):
        with open('pages_traversed.txt', "w") as f:
            f.write(self.get_current_page_number())

    def get_page_from_file(self):
        if os.path.exists('pages_traversed.txt'):
            try:
                with open('pages_traversed.txt', "r") as f:
                    return int(f.read()) + 1
            except:
                return 1
