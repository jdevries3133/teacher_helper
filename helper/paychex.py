import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


CLOCK_STATE_FILE = os.path.join(__file__, 'paychex_clock_state.txt')

class Paychex:
    """
    Clock in and out of paychex from the terminal using selenium. Keep track
    of whether the function has been called today, and issue a reminder if not.

    /var/log/Paychex/clock_state.txt is used to keep track of whether I am
    currently clocked in our out.

    ALWAYS
    """
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.driver = webdriver.Firefox()
        self.clock_state_file = CLOCK_STATE_FILE

    def clock(self):
        """
        A top level function that checks the clock state and the time and performs
        a context-appropriate toggle.
        """
        pass

    def login(self):
        """
        Leaves the driver in the dashboard view.
        """
        self.driver.get('https://myapps.paychex.com/landing_remote/login.do')
        WebDriverWait(self.driver, 10).until(EC.frame_to_be_available_and_switch_to_it(
            self.driver.find_element_by_name('login')
        ))
        username_input = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "USER")))
        username_input.send_keys(self.username)
        self.driver.find_element_by_xpath('/html/body/div[1]/div[2]/div[2]/div[2]/div[1]/div/form/div/div[2]/div[2]/button').click()
        try:
            two_factor_auth_input = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="otpCode"]')))
            two_factor_auth_input.send_keys(input('Enter text verification code.\n'))
            self.driver.find_element_by_xpath('/html/body/div[1]/div[2]/div/div/form/div[2]/div/div/button[2]').click()
        except Exception as e:
            print(e)
            print('fix exception statement with this ^')
        
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.NAME, "PASSWORD"))).send_keys(self.password)
        self.driver.find_element_by_xpath('/html/body/div[1]/div[2]/div/div/div/div/form/div[1]/div[2]/div[2]/button[2]').click()
        self.update_clock_state()

    def clock_in(self):
        """
        Clocks in and updates the clock state.
        """
        pass

    def __toggle_clock(self):
        """
        Private clock in function that will actually press the clock toggle button
        in the browser. Only called by higher functions when necessary conditions
        for the button to be pressed have been met.
        """
        pass

    def clock_out(self):
        """
        Clocks out and updates the clock state.
        """
        pass
    
    def get_clock_state(self):
        """
        Returns the clock state that is LOCALLY CACHED. This may not be accurate,
        but can be used to cue a "are you sure, local storage says you are already
        clocked ___."
        """
        with open(self.clock_state_file, 'r') as txt:
            state = txt.read()
        self.validate(state)
        return state

    def update_clock_state(self, state):
        if state != 'in' or state != 'out':
            raise Exception(
                f'Invalid request. Cannot write {state} to state file.'
            )
        with open(self.clock_state_file, 'w') as txt:
            txt.write(state)
        return 0

    def validate(self, state):
        if len(state.split('\n')) != 1 or state != 'in' or state != 'out':
            open(self.clock_state_file, 'w').close()  # reset state file
            self.login()  # login, which will update state
        return 0