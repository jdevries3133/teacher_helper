from abc import ABC, abstractmethod
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException



class PaychexSeleniumUtils(ABC):
    def __init__(self, username, password, headless=True):
        self.username = username
        self.password = password
        self.headless = headless
        self.driver = None
        self.is_logged_in = False

    def __enter__(self, *args, **kwargs):
        if self.headless:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--window-size=1440x789')
            self.driver = webdriver.Chrome(options=chrome_options)
            return self
        self.driver = webdriver.Chrome()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.driver.quit()

    def _login(self):
        """
        Leaves the driver in the dashboard view.
        """
        self._begin_login()
        self._handle_username()
        self._handle_verification()
        self._handle_password()
        self._post_login_hook()

    def _begin_login(self):
        """
        Navigate to the home page.
        """
        self.driver.get('https://myapps.paychex.com/landing_remote/login.do')
        WebDriverWait(self.driver, 10).until(EC.frame_to_be_available_and_switch_to_it(
            self.driver.find_element_by_name('login')
        ))

    def _handle_username(self):
        """
        Input username
        """
        # username
        username_input = WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.ID, "USER")))
        username_input.send_keys(self.username)
        self.driver.find_element_by_xpath(
            '/html/body/div[1]/div[2]/div[2]/div[2]/div[1]/div/form/div/div[2]/div[2]/button').click()

    def _handle_verification(self):
        """
        Input two factor auth. Use get_otp method from implementation.
        """
        try:
            two_factor_auth_input = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="otpCode"]')))
            sleep(10)  # wait for email to be sent before trying to fetch.
            otp = self.get_otp()
            two_factor_auth_input.send_keys(otp)
            self.driver.find_element_by_xpath(
                '/html/body/div[1]/div[2]/div/div/form/div[2]/div/div/button[2]').click()
        except TimeoutException:
            print('Two factor auth not required')

    def _handle_password(self):
        # password
        WebDriverWait(self.driver, 20).until(EC.presence_of_element_located(
            (By.NAME, "PASSWORD"))).send_keys(self.password)
        self.driver.find_element_by_xpath(
            '/html/body/div[1]/div[2]/div/div/div/div/form/div[1]/div[2]/div[2]/button[2]').click()

    def _post_login_hook(self):
        """
        Cleanup after login process is complete.
        """
        self.driver.switch_to.default_content()
        self.is_logged_in = True
        self.set_cached_clock_state()

    @ abstractmethod
    def set_cached_clock_state(self):
        pass

    @ abstractmethod
    def get_otp(self):
        pass

    def _toggle_clock(self):
        """
        Private clock in function that will actually press the clock toggle button
        in the browser. Only called by higher functions when necessary conditions
        for the button to be pressed have been met.

        Returns clock state after button press.
        """
        self._check_dismiss_modal()
        clock_button = WebDriverWait(self.driver, 40).until(EC.presence_of_element_located(
            (By.XPATH, '//*[@id="stackedinvisibilebutton"]')))
        sleep(1)
        clock_button.click()
        return self._read_site_state()

    def _check_dismiss_modal(self):
        """
        Sometimes a modal window pops up on login and blocks the clock button.
        """
        try:
            dismiss_modal = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        '//*[@id="_pendo-close-guide_"]'
                    )
                )
            )
            dismiss_modal.click()
        except TimeoutException:
            pass

    def _read_site_state(self):
        """
        Private method because it touches the actual site. It reads from the
        site whether the user is currently clocked in.
        """
        if not self.is_logged_in:
            raise Exception(
                'Cannot read site before login'
            )
        status = WebDriverWait(self.driver, 60).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="employeeStatus"]'))).text
        if status == 'Clocked Out':
            return 'out'
        elif 'Working since' in status:
            return 'in'
        else:
            raise Exception(
                '_read_site_state met unexpected condition'
            )
