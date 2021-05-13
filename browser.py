from pathlib import Path
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class CustomBrowser:

    def __init__(self, url):
        self.url = url

    def get_options(self):
        chrome_save_dir = Path(__file__).parent.joinpath('chrome_data').absolute()
        chrome_save_dir.mkdir(exist_ok=True, parents=True)
        options = webdriver.ChromeOptions()
        options.add_argument("--kiosk")
        options.add_argument(r'--user-data-dir={}'.format(chrome_save_dir))
        return options

    def __enter__(self, *args, **kwargs):
        self.browser = webdriver.Chrome(
            chrome_options=self.get_options()
        )
        self.browser.get(self.url)
        time.sleep(3)
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
