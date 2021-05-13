import yaml
from linked_in import Login, Search, ConnectionDialogHandler, SendRequest, ConnectionsIterator
from browser import CustomBrowser


if __name__ == '__main__':
    with open('config.yml') as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    login = Login(data['email'], data['password'])
    search = Search(data['search_query'])
    connection_dialog = ConnectionDialogHandler(data['message'])
    send_request = SendRequest(connection_dialog)
    with CustomBrowser('https://linkedin.com') as browser:
        browser = browser.browser
        login(browser)
        search(browser)
        for name, link, button_elem, elem_id in ConnectionsIterator(browser):
            print(
                f'trying sending request to name: {name}\nlink: {link}\nbutton: {button_elem}')
            send_request(browser, name, link, button_elem, elem_id)
