import os

from .paychex import Paychex
from .imap import Imap, PaychexOTPNotFound


class PaychexOTP(Paychex):
    """
    Subclass of Paychex that gets one time passwords from a specific email folder,
    assuing that emails are forwarded from a user's phone automatically.
    """

    def __init__(
            self, *a, username: str, password: str,
            mailbox: str='Paychex', **kw):
        super().__init__(*a, **kw)
        self.username = username
        self.password = password
        self.mailbox = mailbox

    def get_otp(self) -> str:
        try:
            username = os.getenv('EMAIL_USERNAME')
            password = os.getenv('EMAIL_PASSWORD')
            if username and password:
                return Imap(
                    username,
                    password,
                    mailbox=self.mailbox
                ).get_paychex_otp()
            else:
                print(
                    'WARNING: Automatic one-time-password-fetch from email is not '
                    'properly configured. If you follow these steps, this '
                    'module can\nautomatically fetch the paychex one-time-'
                    'passcode from your email and log you in:\n'
                    '\t*  Get an app on your phone to automatically forward '
                    'emails from paychex\n\tto your email. I use LanrenSMS for Android\n'
                    '\t* Set an email filter to put those emails into an inbox '
                    'called "Paychex".\n\tIt\'s also a good idea to '
                    'Set that filter to make the emails skip your inbox '
                    'So that you don\'t get spammed.\n'
                    '\t* Set your email username and password as environment '
                    'variables on your system.\n\tThe variable names '
                    'should be "EMAIL_USERNAME", and "EMAIL_PASSWORD".\n\t'
                    'for gmail, set up 2FA and create an app password:\n\t'
                    'https://support.google.com/accounts/answer/185833?hl=en\n'

                    '\t* After that, it should just work.\n\n'

                    'Alternatively, subclass Paychex and rewrite the '
                    'get_otp method. It takes no arguments, and returns the '
                    'otp as a string.\nBy default, it tries to find your '
                    'email username and password and to auto-fetch the '
                    'passcode, and falls back on input().'
                )
                return input('\n\n\nSince automatic otp fetching is not setup, enter the otp sent to your phone now:\n')
        except PaychexOTPNotFound:
            return super().get_otp()
