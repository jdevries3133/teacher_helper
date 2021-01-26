from datetime import datetime
from email import message_from_bytes
from email.utils import parsedate_to_datetime
from imaplib import IMAP4_SSL
import os
from time import sleep
import re


class PaychexOTPNotFound(Exception):
    pass


class Imap(IMAP4_SSL):
    def __init__(self, username, password, mailbox='Paychex'):
        super().__init__('imap.gmail.com')
        self.login(
            username,
            password
        )
        self.mailbox = mailbox

    def get_paychex_otp(self, recursion_depth=0):
        """
        OTP Getter will always fetch the newest one time password email. If the
        email is older than 5 minutes, it will wait 10 seconds and try again for
        a fresh one.
        """
        _, raw_msg_count = self.select('Paychex')
        msg_count = int(raw_msg_count[0])
        if not msg_count:
            sleep(10)
            return self.get_paychex_otp((recursion_depth + 1))
        _, messages = self.fetch(str(msg_count), '(RFC822)')
        message = messages[0]
        if not message[1]:
            sleep(10)
            return self.get_paychex_otp((recursion_depth + 1))
        msg = message_from_bytes(message[1])
        msg_date = parsedate_to_datetime(msg.get('Date'))
        msg_age = datetime.now().timestamp() - msg_date.timestamp()
        if msg_age > 300:
            print('Paychex otp not found in email. Waiting 10s and trying again...')
            sleep(10)
            if recursion_depth > 10:
                raise PaychexOTPNotFound(
                    'No Paychex OTP was found in your email')
            return self.get_paychex_otp((recursion_depth + 1))
        payload = msg.get_payload()
        pattern = re.compile(r'temporary verification code is: ((\d){5})\.')
        mo = re.search(pattern, payload)
        if mo:
            print(f'OTP "{mo[1]}" automatically retrieved.')
            return mo[1]
        raise PaychexOTPNotFound(
            f'No regex match for the following message:\n\n{payload}'
        )
