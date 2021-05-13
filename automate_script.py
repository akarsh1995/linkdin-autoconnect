from pathlib import Path
import time
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from random import randint

def random_gaps0_5():
    sleep(randint(0, 5))


class CustomBrowser:

    def get_options(self):
        chrome_save_dir = Path(__file__).parent.joinpath('chrome_data').absolute()
        chrome_save_dir.mkdir(exist_ok=True, parents=True)
        options = webdriver.ChromeOptions()
        options.add_argument("--kiosk")
        print(chrome_save_dir)
        options.add_argument(r'--user-data-dir={}'.format(chrome_save_dir))
        return options

    def __enter__(self, *args, **kwargs):
        self.base_url = 'https://www.linkedin.com'
        self.browser = webdriver.Chrome(
            chrome_options=self.get_options()
        )
        self.browser.get(self.base_url)
        sleep(3)
        return self

    def __exit__(self, *args, **kwargs):
        self.browser.quit()


class BaseAction:
    browser: webdriver.Chrome

    xpath_body =  '//body'

    def page_down(self, times=1):
        for _ in range(times):
            self.send_keys(Keys.PAGE_DOWN, self.xpath_body)
            time.sleep(0.5)

    def page_up(self):
        self.send_keys(Keys.PAGE_UP, self.xpath_body)
        time.sleep(0.5)

    def adjust_window(self, index):
        self.browser.execute_script(
            '''window.scrollTo(0,{});'''.format(
                110 * index
            )
        )
        time.sleep(0.5)

    def send_keys(self, xpath, keys):
        return self.browser.find_element_by_xpath(xpath).send_keys(keys)

    def open_new_tab(self):
        self.browser.execute_script('''window.open("","_blank");''')
        self.tabs = self.browser.window_handles
        self.browser.switch_to.window(self.tabs[1])

    def close_and_switch_tab(self):
        self.browser.close()
        self.browser.switch_to.window(self.tabs[0])
        time.sleep(0.5)

    def wait_and_click(self, xpath):
        self.wait_and_get_elem(xpath).click()

    def wait_and_send_keys(self, xpath, keys):
        self.wait_and_get_elem(xpath).send_keys(keys)

    def wait_and_get_elem(self, xpath, duration=10):
        return WebDriverWait(self.browser, duration).until(
            EC.element_to_be_clickable(
                (By.XPATH, xpath)
            ))

    def wait_and_check_presence(self, xpath, timeout=3):
        try:
            WebDriverWait(self.browser, timeout).until(
                EC.visibility_of_element_located((
                    (By.XPATH, xpath)
                )))
            return True
        except:
            return False

    def action(self):
        NotImplemented

    def __call__(self, browser):
        self.browser = browser
        return self.action()


class Login(BaseAction):
    browser = webdriver.Chrome
    base_url = 'https://linkedin.com'
    remmber_me_button = '//button[text()="Remember"]'
    logged_in_hook = '//span[text()="Who viewed your profile"]'

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

    def __init__(self, text_note):
        self.text_note = text_note

    def action(self):
        self.wait_and_click(self.xpath_add_note)
        random_gaps0_5()
        self.wait_and_send_keys(self.xpath_message_text_box, self._text_note)
        random_gaps0_5()
        self.wait_and_click(self.xpath_send_button)

    def __call__(self, browser, name):
        name = name.encode('ascii', 'replace').decode().replace('?', '').strip()
        self._text_note = self.text_note.format(name)
        return super().__call__(browser)


class SendRequest(BaseAction):

    def __init__(self, name, link,  button, element_id,
                 connection_dialogue_handler: ConnectionDialogHandler):
        self.link = link
        self.name = name
        self._button = button
        self.element_id = element_id
        self.connection_dialogue_handler = connection_dialogue_handler

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
    xpath_profile_image = '//img[@width="48"]'
    xpath_next_button = '//span[text()="Next"]'

    def __init__(self, browser):
        self.browser = browser

    def __iter__(self):
        while True:
            if self.wait_and_check_presence(self.xpath_profile_image):
                profile_pic_elems = self.browser.find_elements_by_xpath(self.xpath_profile_image)
                sleep(2)
                for index, profile_pic_elem in enumerate(profile_pic_elems):
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


if __name__ == '__main__':
    with CustomBrowser() as browser:
        browser = browser.browser
        login = Login('akarsh.1995.02@gmail.com', 'Linkedin@4914')
        login(browser)
        Search('Artificial Intelligence')(browser)
        dia_handler = ConnectionDialogHandler('''Hello {}, I'm looking forward to connect with you.''')
        for name, link, button_elem, elem_id in ConnectionsIterator(browser):
            print(f'sending  request to name: {name}\nlink: {link}\nbutton: {button_elem}')
            s = SendRequest(
                name,
                link,
                button_elem,
                elem_id,
                dia_handler
            )
            s(browser)
