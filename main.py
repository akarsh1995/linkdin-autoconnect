from automate_script import SendRequests

if __name__ == '__main__':
    message = input('Enter the text you\'d like to send')
    s = SendRequests(message)
    s.login()
    s.switch_to_people()
    s.send_requests()
