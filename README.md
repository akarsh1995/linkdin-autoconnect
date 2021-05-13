# LinkedIn auto connection request sender.

This project aims to help you automate sending connection request procedure on LinkedIn.

You need to download the chrome webdriver binary from the official website. 

https://chromedriver.chromium.org/downloads matching with the installed version of the google chrome.

Copy the obtained binary in the *./webdriver* directory in your project root dir.

Set the message and search field inputs in the main.py file.

To run the script create a python virtual environment and install the requirements using the below command and then run:

* Enter the credentials and rename sample_config.yml to config.yml

```sh
pipenv install
pipenv run python ./automate_script.py
```
