from automate_script import SendRequests

if __name__ == '__main__':
    message = 'The field of your work quite excites me especially AI/ML. Would love to stay connected for the updates.\n-Regards\nAkarsh Jain.'
    s = SendRequests(message)
    s.login()
    s.search("Machine learning Artificial Intelligence Bangalore")
    s.switch_to_people()
    s.jump_to(page_no=22)
    s.send_requests()
