from automate_script import SendRequests, gap_1s

if __name__ == '__main__':
    message = 'The field of your work quite excites me especially AI/ML. Would love to stay connected for the updates.\n-Regards\nAkarsh Jain.'
    s = SendRequests(message)
    s.login()
    s.search("Artificial Intelligence CEO")
    gap_1s()
    s.switch_to_people()
    try:
        while True:
            try:
                s.jump_to(page_no=s.get_page_from_file())
                s.send_requests()
            except:
                print(s.browser.current_url, 'posed some error.')
    except KeyboardInterrupt:
        print('interrupted')
    finally:
        s.close_browser()
