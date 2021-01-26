from datetime import datetime
import os

from .util import PaychexSeleniumUtils


CLOCK_STATE_FILE = os.path.join(
    os.path.dirname(__file__), 'clock_state.txt')
CHROME_DRIVER_PATH = os.path.join(os.path.dirname(__file__), 'chromedriver')


def login_first(func):
    def wrapper(*args):
        if not args[0].is_logged_in:
            args[0].login()
        func(args[0])
    return wrapper


class Paychex(PaychexSeleniumUtils):
    """
    Clock in and out of paychex from the terminal using selenium. Keep track
    of whether the function has been called today, and issue a reminder if not.

    /var/log/Paychex/clock_state.txt is used to keep track of whether I am
    currently clocked in our out.

    ALWAYS

    Note: After login, the web driver is left with the inner html document
    selected.
    """
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.clock_state_file = CLOCK_STATE_FILE
        self.clock_state = self.get_clock_state()

    def login(self):
        super()._login()

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
                choice = input(
                    'Would you like to clock in or out? (enter "in" or "out")\n'
                )
                if choice == 'in':
                    self.clock_in()
                    break
                if choice == 'out':
                    self.clock_out()
                    break
                print('Enter "in" or "out"\n')

    @ staticmethod
    def get_otp():
        otp = input('Enter text verification code.\n')
        return otp

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
            self._toggle_clock()
        self.set_cached_clock_state()
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
            self._toggle_clock()
        self.set_cached_clock_state()
        print('Clock out successful')
        self.driver.close()

    def get_clock_state(self):
        """
        Returns the clock state that is LOCALLY CACHED. This may not be accurate,
        but can be used to cue a "are you sure, local storage says you are already
        clocked ___."
        """
        return self._read_cached_state()

    @login_first
    def set_cached_clock_state(self):
        """
        Sets local state and self attribute to new state
        """
        state = self._read_site_state()
        self.clock_state = state
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
        try:
            with open(self.clock_state_file, 'r') as txt:
                state = txt.read().strip()
        except FileNotFoundError:
            return 'unknown'
        if state != 'in' and state != 'out':
            if not self.is_logged_in:
                self.login()
            state = self._read_site_state()
            self._update_cached_state(self._read_site_state())
        return 0
