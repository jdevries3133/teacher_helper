from datetime import datetime
import os
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

from .imap import Imap


CLOCK_STATE_FILE = os.path.join(os.path.dirname(__file__), 'paychex_clock_state.txt')
CHROME_DRIVER_PATH = os.path.join(os.path.dirname(__file__), 'chromedriver')


def login_first(func):
    def wrapper(*args):
        if not args[0].is_logged_in:
            args[0].login()
        func(args[0])
    return wrapper

class Paychex:
    """
    Clock in and out of paychex from the terminal using selenium. Keep track
    of whether the function has been called today, and issue a reminder if not.

    /var/log/Paychex/clock_state.txt is used to keep track of whether I am
    currently clocked in our out.

    ALWAYS

    Note: After login, the web driver is left with the inner html document
    selected.
    """
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.is_logged_in = False
        self.clock_state_file = CLOCK_STATE_FILE
        self.clock_state = self.get_clock_state()
        # init chrome driver
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--window-size=1440x789')
        self.driver = webdriver.Chrome(options=chrome_options)

    def clock(self):
        """
        A top level function that checks the clock state and the datetime and
        performs a context-appropriate toggle.
        """
        now = datetime.now()
        is_weekday = now.weekday() < 5
        is_am = 6 < now.hour < 11
        is_pm = 12 < now.hour < 18
        if is_weekday and is_am:
            print('Clocking in')
            self.clock_in()
        elif is_weekday and is_pm:
            print('Clocking out')
            self.clock_out()
        else:
            choice = None
            while not choice == 'in' or not choice == 'out':
                choice = input('Would you like to clock in or out?\n')
                if choice == 'in':
                    self.clock_in()
                    break
                else:
                    self.clock_out()
                    break
                print('Enter "in" or "out"\n')

    def login(self):
        """
        Leaves the driver in the dashboard view.
        """
        self.driver.get('https://myapps.paychex.com/landing_remote/login.do')
        WebDriverWait(self.driver, 10).until(EC.frame_to_be_available_and_switch_to_it(
            self.driver.find_element_by_name('login')
        ))
        # username
        username_input = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.ID, "USER")))
        username_input.send_keys(self.username)
        self.driver.find_element_by_xpath('/html/body/div[1]/div[2]/div[2]/div[2]/div[1]/div/form/div/div[2]/div[2]/button').click()
        # 2-Factor Auth (may not be necessary)
        try:
            two_factor_auth_input = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="otpCode"]')))
            sleep(10)
            try:
                otp = Imap(
                    os.getenv('GMAIL_USERNAME'),
                    os.getenv('GMAIL_PASSWORD'),
                ).get_paychex_otp()
            except:
                otp = input('Enter text verification code.\n')
            two_factor_auth_input.send_keys(otp)
            self.driver.find_element_by_xpath('/html/body/div[1]/div[2]/div/div/form/div[2]/div/div/button[2]').click()
        except:
            pass
        # password
        WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.NAME, "PASSWORD"))).send_keys(self.password)
        self.driver.find_element_by_xpath('/html/body/div[1]/div[2]/div/div/div/div/form/div[1]/div[2]/div[2]/button[2]').click()
        # reset frame
        self.driver.switch_to.default_content()
        self.is_logged_in = True
        self.set_clock_state(self._read_site_state())
        return 0

    @login_first
    def clock_in(self):
        """
        Clocks in and updates the clock state.
        """
        if self.clock_state == 'in':
            input(
                'Are you sure? According to the local cache, you are already\n'
                'clocked in.'
            )
        site_state = self._read_site_state()
        if site_state == 'out':
            new_state = self._toggle_clock()
        self.set_clock_state(new_state)
        print('Clock in successful')
        self.driver.close()

    @login_first
    def clock_out(self):
        """
        Clocks out and updates the clock state.
        """
        if self.clock_state == 'out':
            input(
                'Are you sure? According to the local cache, you are already\n'
                'clocked out.'
            )
        site_state = self._read_site_state()
        if site_state == 'in':
            new_state = self._toggle_clock()
        self.set_clock_state(new_state)
        print('Clock out successful')
        self.driver.close()
    
    def get_clock_state(self):
        """
        Returns the clock state that is LOCALLY CACHED. This may not be accurate,
        but can be used to cue a "are you sure, local storage says you are already
        clocked ___."
        """
        return self._read_cached_state()

    def set_clock_state(self, state):
        """
        Sets local state and self attribute to new state
        """
        state = self._read_site_state()
        self.new_state = state
        self._update_cached_state(state)
        return state

    def _update_cached_state(self, update):
        if update != 'in' and update != 'out':
            raise ValueError(
                f'{update} is an invalid update request'
            )
        with open(self.clock_state_file, 'w') as txt:
            txt.write(update)
        return update

    def _read_cached_state(self):
        with open(self.clock_state_file, 'r') as txt:
            state = txt.read().strip()
        if state != 'in' and state != 'out':
            if not self.is_logged_in:
                self.login()
            state = self._read_site_state()
            self._update_cached_state(self._read_site_state())
        return 0

    def _toggle_clock(self):
        """
        Private clock in function that will actually press the clock toggle button
        in the browser. Only called by higher functions when necessary conditions
        for the button to be pressed have been met.

        Returns clock state after button press.
        """
        if not self.is_logged_in:
            raise Exception(
                'Cannot read site before login'
            )
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="stackedinvisibilebutton"]'))).click()
        return self._read_site_state()

    def _read_site_state(self):
        """
        Private method because it touches the actual site. It reads from the
        site whether the user is currently clocked in.
        """
        if not self.is_logged_in:
            raise Exception(
                'Cannot read site before login'
            )
        status = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="employeeStatus"]'))).text
        if status == 'Clocked Out':
            return 'out'
        elif 'Working since' in status:
            return 'in'
        else:
            raise Exception(
            '_read_site_state met unexpected condition'
            )

