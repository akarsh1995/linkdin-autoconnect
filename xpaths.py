class NavigationXpaths:
    add_note_button_xpath = '//*[text()="Add a note"]'
    add_text_xpath = '//textarea[@class="send-invite__custom-message mb3 ember-text-area ember-view"]'
    invite_send_button_xpath = '//*[text()="Send invitation"]'
    cancel_button_xpath = '//button[@aria-label="Dismiss"]'
    profile_div = '//div[@data-test-search-result="PROFILE"]'
    button_text_xpath = '(//div[@data-control-name="srp_profile_actions"]/button)|(//div[' \
                        '@class="search-result__actions"]/div/button)|//li-icon[@type="lock-icon"]/parent::* '

    profile_link_xpath = '//div[@class="search-result__info pt3 pb4 ph0"]'
    button_click_xpath = '((//div[@class="search-result__wrapper"])[{}]//button)|//li-icon[@type="lock-icon"]/parent::*'
    next_button_xpath = '//span[text()="Next" and @class="artdeco-button__text"]'

    search_bar_xpath = '//input[@placeholder="Search"]'
    people_button_xpath = '//span[text()="People"]'

    connect_button_on_profile_xpath = '//span[@class="artdeco-button__text" and text()="Connect"]'
    more_button_xpath = '//span[@class="artdeco-button__text" and text()="More…"]'
    more_button_connect_xpath = '//span[@class="display-flex t-normal pv-s-profile-actions__label" and text(' \
                                ')="Connect"] '

    body_xpath = '//body'
    current_page_number_text = '//li/span[@aria-current="true"]/text()'
    all_filters = '//span[text()="All Filters"]'
    second_connection_checkbox = '//label[text()="2nd"]'
    second_degree_apply = '//button[@data-control-name="all_filters_apply"]/span[text()="Apply"]'
