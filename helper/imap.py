from datetime import datetime
from email import message_from_bytes
from email.header import decode_header
from email.utils import parsedate_to_datetime
from imaplib import IMAP4_SSL
import os
from time import sleep
import re
import sys


class Imap(IMAP4_SSL):
    def __init__(self, username, password):
        super().__init__('imap.gmail.com')
        self.login(
            username,
            password
        )

    def get_paychex_otp(self, recursion_depth=0):
        """
        OTP Getter will always fetch the newest one time password email. If the
        email is older than 5 minutes, it will wait 10 seconds and try again for
        a fresh one.
        """
        status, raw_msg_count = self.select('Paychex')
        msg_count = int(raw_msg_count[0])
        if not msg_count:
            sleep(10)
            return self.get_paychex_otp()
        status, messages = self.fetch(str(msg_count), '(RFC822)')
        message = messages[0]
        msg = message_from_bytes(message[1])
        msg_date = parsedate_to_datetime(msg.get('Date'))
        msg_age = datetime.now().timestamp() - msg_date.timestamp()
        if msg_age > 300:  # change back to 300 later
            print('Paychex otp not found in email. Waiting 10s and trying again...')
            sleep(10)
            if recursion_depth > 10:
                print('No otp was found in your email after six tries in the past minute. Exiting now.')
                sys.exit()
            return self.get_paychex_otp((recursion_depth + 1))
        payload = msg.get_payload()
        pattern = re.compile(r'temporary verification code is: ((\d){5})\.')
        mo = re.search(pattern, payload)
        if mo:
            print(f'OTP "{mo[1]}" automatically retrieved.')
            return mo[1]
        else:
            raise Exception(
                f'No regex match for the following message:\n\n{payload}'
            )
    
if __name__ == '__main__':
    im = Imap(
        os.getenv('GMAIL_USERNAME'),
        os.getenv('GMAIL_PASSWORD')
    )
    im.get_paychex_otp()